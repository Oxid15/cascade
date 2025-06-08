from cascade.lines import ModelLine
from cascade.models import BasicModel

if __name__ == "__main__":
    print("Hello!")
    print("I am example log")

    model = BasicModel()
    model.add_log()

    line = ModelLine("log_tracking_example")
    line.save(model)
