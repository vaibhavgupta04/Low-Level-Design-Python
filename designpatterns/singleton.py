class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# ----------- Usage -------------
if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()

    print(s1 is s2)  # True


# __init__ is an instance method, while __new__ is a static method.
# __new__ is responsible for creating and returning a new instance (object), while __init__ is responsible for initializing the attributes of the newly created object.
# __new__ is called before __init__.
# __new__ happens first, then __init__.
# __new__ can return any object, while __init__ must return None.

class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    

if __name__ == "__main__":
    s1 = Singleton()
    s2 = Singleton()
    
    print(s1 is s2)