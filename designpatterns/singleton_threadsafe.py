import threading

class ThreadSafeSingleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # double-check
                    cls._instance = super().__new__(cls)
        return cls._instance

# ----------- Usage -------------
if __name__ == "__main__":
    a = ThreadSafeSingleton()
    b = ThreadSafeSingleton()
    print(a is b)  # True


# __init__ is an instance method, while __new__ is a static method.
# __new__ is responsible for creating and returning a new instance (object), while __init__ is responsible for initializing the attributes of the newly created object.
# __new__ is called before __init__.
# __new__ happens first, then __init__.
# __new__ can return any object, while __init__ must return None.