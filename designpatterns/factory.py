from abc import ABC, abstractmethod

# Product Interface
class Shape(ABC):
    @abstractmethod
    def draw(self):
        pass

# Concrete Products
class Circle(Shape):
    def draw(self):
        return "Drawing Circle"

class Square(Shape):
    def draw(self):
        return "Drawing Square"

class Rectangle(Shape):
    def draw(self):
        return "Drawing Rectangle"

# Factory
class ShapeFactory:
    @staticmethod
    def get_shape(shape_type: str) -> Shape:
        shape_type = shape_type.lower()
        if shape_type == "circle":
            return Circle()
        elif shape_type == "square":
            return Square()
        elif shape_type == "rectangle":
            return Rectangle()
        else:
            raise ValueError("Unknown shape type")


# ----------- Usage -------------
if __name__ == "__main__":
    factory = ShapeFactory()

    circle = factory.get_shape("circle")
    print(circle.draw())

    square = factory.get_shape("square")
    print(square.draw())

    rectangle = factory.get_shape("rectangle")
    print(rectangle.draw())
