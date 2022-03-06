import inspect


def error_trace(*objs, stack_index: int = 1):
    """Returns a quick trace to the calling namespace for a function/method,
    in case of an error.  Object instances supplied to *objs have their
    class names prepended to the message, separated by '.' characters.
    """
    objects = [o.__class__.__name__ for o in objs]
    calling_func = inspect.stack()[stack_index].function
    if len(objects) > 0:
        return f"{'.'.join(objects)}.{calling_func}"
    return f"{calling_func}"


def error_trace_alt(self_name: str = "self",
                    cls_name: str = "cls",
                    stack_index: int = 1) -> str:
    stack = inspect.stack()
    if len(stack) < stack_index + 1:
        return ""
    parentframe = stack[stack_index][0]
    name = []

    # get module name (if applicable)
    module = inspect.getmodule(parentframe)
    if module:  # module can be None if executed directly in console
        name.append(module.__name__)

    # get class name (if applicable and not static)
    if self_name in parentframe.f_locals:  # for regular methods
        name.append(parentframe.f_locals[self_name].__class__.__name__)
    elif cls_name in parentframe.f_locals:  # for classmethods
        name.append(parentframe.f_locals[cls_name].__class__.__name__)

    # get function/method name
    callable_name = parentframe.f_code.co_name
    if callable_name != "<module>":
        name.append(callable_name)

    # avoid circular refs and frame leaks
    del parentframe, stack
    return ".".join(name)
