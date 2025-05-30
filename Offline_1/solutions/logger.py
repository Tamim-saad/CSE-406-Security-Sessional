class Logger:
  def __init__(self, isLogging = True):
    self.isLogging = isLogging
  
  def log(self, message: str):
    if self.isLogging:
      print(message)
  
  def setIsLogging(self, isLogging: bool):
    self.isLogging = isLogging