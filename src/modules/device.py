class Device:
    isDefault: bool  # is Default device?
    index: int  # index of audio device (sd.query_devices(index))
    name: str  # audio device name
    inout_info: str  # "input" or "ouput" device?
    input_count: int  # number of inputs
    output_count: int  # number of outputs
    driver: str  # Sound Driver (MME, WDM, ASIO...)

    def __init__(self, isdefault=False, index=0, name="", input_count=0, output_count=0, driver=""):
        self.isDefault = isdefault
        self.index = index
        self.name = name
        self.inout_info = ""
        self.input_count = input_count
        self.output_count = output_count
        self.driver = driver

    def print_dict(self):
        print(
            f"{self.isDefault} {self.index}: {self.name} [{self.driver} {self.inout_info}] ({self.input_count} In, {self.output_count} Out)")

    def __repr__(self):
        return f"{self.isDefault} {self.index}: {self.name} [{self.driver} {self.inout_info}] ({self.input_count} In, {self.output_count} Out)"

    def __str__(self):
        return f"{self.isDefault} {self.index}: {self.name} [{self.driver} {self.inout_info}] ({self.input_count} In, {self.output_count} Out)"


class MicDevice(Device):
    def __init__(self, isdefault=False, index=0, name="", input_count=0, output_count=0, driver=""):
        super().__init__(isdefault, index, name, input_count, output_count, driver)
        self.inout_info = "input"


class SpeakerDevice(Device):
    def __init__(self, isdefault=False, index=0, name="", input_count=0, output_count=0, driver=""):
        super().__init__(isdefault, index, name, input_count, output_count, driver)
        self.inout_info = "output"


if __name__ == "__main__":
    device = SpeakerDevice(False,0,"test",1,2,"MME")
    print(device)