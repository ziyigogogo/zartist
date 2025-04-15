import asyncio
import json
from zartist.clients.qwen_vl_max import QwenVLClient
from zartist.mcp.pokder.client import prepare_tools
from zartist.mcp.pokder.client import Client


class QwenFunctionCallClient(QwenVLClient):
    """QwenVLClient 子类，支持 function calling 闭环自动管理 messages，异步调用 pokder client 工具"""

    def build_request(self, messages, tools=None, tool_choice="auto"):
        req = super().build_request(messages)
        if tools is not None:
            req["tools"] = tools
            req["tool_choice"] = tool_choice
        return req

    async def call_tool(self, tool_call, pokder_client):
        name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        try:
            result = await pokder_client.call_tool(name, arguments)
            print("call tool result: ", result[0].text)
            return result[0].text
        except Exception as e:
            return f"Tool {name} error: {str(e)}"

    async def get_content(self,
                          response,
                          messages,
                          pokder_client,
                          tools=None,
                          tool_choice="auto",
                          max_loops=5,
                          verbose=True) -> str:
        dict_resp = response.to_dict()
        if verbose:
            print(dict_resp)
        self.usage_summary(dict_resp["usage"])
        message = dict_resp["choices"][0]["message"]
        messages.append(message)
        loop_count = 0
        while "tool_calls" in message and message["tool_calls"] and loop_count < max_loops:
            for tool_call in message["tool_calls"]:
                tool_response = await self.call_tool(tool_call, pokder_client)
                messages.append({"role": "tool", "tool_call_id": tool_call["id"], "content": str(tool_response)})
            req = self.build_request(messages, tools=tools, tool_choice=tool_choice)
            print("tool call request", req)
            response = self.send_request(req)
            dict_resp = response.to_dict()
            if verbose:
                print(dict_resp)
            self.usage_summary(dict_resp["usage"])
            message = dict_resp["choices"][0]["message"]
            messages.append(message)
            loop_count += 1
        return message.get("content", "")


async def main():
    tools = await prepare_tools()
    prompt = "图中画了什么？最有可能的地点在世界上的哪个国家的哪个景区？并帮我查询一下那个景区未来的天气情况"
    image_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"
    llm = QwenFunctionCallClient()
    messages = llm.build_messages(prompt=prompt, image_reprs=image_url)
    req = llm.build_request(messages, tools=tools)
    resp = llm.send_request(req)
    async with Client(
            r"C:\\Users\\admin\\Desktop\\projects\\zartist\\zartist\\mcp\\pokder\\server.py") as pokder_client:
        final_answer = await llm.get_content(resp, messages, pokder_client, tools=tools)
        print("最终答案：", final_answer)


if __name__ == "__main__":
    asyncio.run(main())
