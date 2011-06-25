def calculateDamage(damage, defense):
  num = damage - defense * 0.5
  if num < 1.0:
    num = 1.0
  return num

def clamp(value, minValue, maxValue):
  return max(minValue, min(maxValue, value))

