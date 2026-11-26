import pyvisa

rm = pyvisa.ResourceManager("@py")
inst = rm.open_resource("ASRL/dev/cu.usbmodem21101::INSTR")
inst.baud_rate = 115200          # dopasuj do urządzenia
inst.read_termination = "\n"
inst.write_termination = "\n"
inst.timeout = 3000

print(inst.query("*IDN?"))

# 939770.0 15.245331 -0.012662731 21.22647 -0.036052592 21.931182 -0.033003964 22.676116 -0.039424208 22.516968
# 1 - znacznik czasowy milisekundy
# 2 - temperatura platformy
# dodć czułość klibracj
# pary napięcie - temp (temp wyliczyć z róznicy) s, e, n, w (