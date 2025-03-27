import inspect


def args2kwargs(*args, **kwargs):
    """获取调用此函数的函数的所有输入参数
    
    Returns:
        dict: 包含所有参数的字典
    """
    # 获取调用者的帧
    caller_frame = inspect.currentframe().f_back
    try:
        # 获取调用者函数的参数信息
        arg_info = inspect.getargvalues(caller_frame)
        # 获取所有参数名（除了self）
        arg_names = [arg for arg in arg_info.args if arg != 'self']
        # 创建一个包含所有参数的字典
        all_args = {}
        # 添加位置参数
        for i, name in enumerate(arg_names):
            if i < len(args):
                all_args[name] = args[i]
            elif name in arg_info.locals:
                all_args[name] = arg_info.locals[name]
        # 添加关键字参数
        all_args.update(kwargs)
        return all_args
    finally:
        # 清理引用，避免循环引用
        del caller_frame
