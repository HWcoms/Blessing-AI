import inspect
import os

logging = True


def print_log(log_type="log", text="", detail_text="", print_func_name=True):
    """print logs by types ['log', 'error', 'warning']
      Args:
        log_type: ['log', 'error', 'warning']   (:py:class:`str`)
        text: first message to print    (:py:class:`str`)
        detail_text: second message to print    (:py:class:`str`)
        print_func_name: print name of  function  at front?  (:py:class:`boolean`)
    """
    if not logging:
        return

    prefix = ""
    _result = text

    _first_col, _second_col = None, None
    if log_type == "log":
        _first_col = "\033[34m"
        _second_col = "\033[32m"
    elif log_type == "error":
        _first_col = "\033[31m"
        _second_col = "\033[33m"
        prefix = "Error! "
    elif log_type == "warning":
        _first_col = "\033[33m"
        _second_col = "\033[32m"
        prefix = "Warning! "

    if print_func_name:
        file_name = os.path.basename(inspect.stack()[1].filename)
        file_name = file_name.replace(".py", "")

        _result = f"[{prefix}{file_name}.{inspect.stack()[1].function}]: {_result}"

    if detail_text != "" and detail_text:
        _result = f"{_result}: {_second_col}{detail_text}"

    print(_first_col + _result + "\033[0m")

    return inspect


def fix_uri_to_print(path_str, log_msg: str = ""):
    prefix = "file:///"
    fixed_path = prefix + path_str.replace(os.sep, '/')

    if log_msg != "":
        print(f"{log_msg}: {fixed_path}")
    return fixed_path


if __name__ == "__main__":
    print_log("log", "test", "test_detail")
