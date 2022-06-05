class Bonnet():
  def __init__(self, setupDisplay=False, width=240, height=240, rotation=180):
    self.height = height
    self.width = width
    self.rotation = rotation
    self.display = None
    self.buttons = {}
    self.setup(setupDisplay=setupDisplay)

  # Setup the Display and get a display object
  def setup(self, setupDisplay):
    if setupDisplay:
      import board
      from digitalio import DigitalInOut, Direction
      import adafruit_rgb_display.st7789 as st7789

      print("Setting up Adafruit st7789 driver...")
      # Create the display
      cs_pin = DigitalInOut(board.CE0)
      dc_pin = DigitalInOut(board.D25)
      reset_pin = DigitalInOut(board.D24)
      BAUDRATE = 24000000

      spi = board.SPI()
      self.display = st7789.ST7789(
        spi,
        width=self.width,
        height=self.height,
        y_offset=80,
        rotation=self.rotation,
        cs=cs_pin,
        dc=dc_pin,
        rst=reset_pin,
        baudrate=BAUDRATE
      )
      # Get the Adafruit 1.3" TFT Bonnet Buttons
      # Input pins:
      button_A = DigitalInOut(board.D5)
      button_A.direction = Direction.INPUT

      button_B = DigitalInOut(board.D6)
      button_B.direction = Direction.INPUT

      button_L = DigitalInOut(board.D27)
      button_L.direction = Direction.INPUT

      button_R = DigitalInOut(board.D23)
      button_R.direction = Direction.INPUT

      button_U = DigitalInOut(board.D17)
      button_U.direction = Direction.INPUT

      button_D = DigitalInOut(board.D22)
      button_D.direction = Direction.INPUT

      button_C = DigitalInOut(board.D4)
      button_C.direction = Direction.INPUT

      self.buttons['A'] = button_A
      self.buttons['B'] = button_B
      self.buttons['LEFT'] = button_L
      self.buttons['RIGHT'] = button_R
      self.buttons['UP'] = button_U
      self.buttons['DOWN'] = button_D
      self.buttons['STICK'] = button_C      
    else:
      print("Not using Adafruit Driver.")

  def enableBacklight(self, onOff=True):
    # Turn on the Backlight
    if self.display:
      backlight = DigitalInOut(board.D26)
      backlight.switch_to_output()
      backlight.value = onOff
    else:
      print("No display setup. Unable to setup backlight.")
