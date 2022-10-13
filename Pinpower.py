from machine import mem32

PADS_BANK0_BASE     = 0x4001C000

PAD_GPIO            = PADS_BANK0_BASE + 0x04 # Add (pin * 4)
PAD_GPIO_MPY        = 4

PAD_DRIVE_BITS      = 4 # 0=2mA, 1=4mA, 2=8mA, 3=12mA   Default=1, 4mA drive

def SetPinDriveStrength(pin, mA):
  adr = PAD_GPIO + PAD_GPIO_MPY * pin
  mem32[adr] &= 0xFFFFFFFF ^ ( 0b11 << PAD_DRIVE_BITS)
  if   mA <= 2 : mem32[adr] |= 0b00 << PAD_DRIVE_BITS
  elif mA <= 4 : mem32[adr] |= 0b01 << PAD_DRIVE_BITS
  elif mA <= 8 : mem32[adr] |= 0b10 << PAD_DRIVE_BITS
  else         : mem32[adr] |= 0b11 << PAD_DRIVE_BITS

SetPinDriveStrength(18, 12) # Set drive strenth to 12mA
