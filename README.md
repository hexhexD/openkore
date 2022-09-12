## Tweaks

* Run XKore 1 on a differnt machine.
  1. Guest can access host using adapter ip. It's better than the next two methods.
  2. XKore server binds to 0.0.0.0 under NAT and port forwarding,
  3. XKore server binds to 0.0.0.0 under briged and NetRedirect.dll points to virtual machine ip

* Using patched MinHook
* Commented out processGetPlayerInfo() in CoreLogic.pm
* Need to update this ptr and function offset of all manual functions
* Enable logging flag to see what the client sends
* Hook on encryptAndSend is detected.

## Notes
* Ragnarok won't launch if wxstart.exe is running, privelage of wxstart.exe doesn't matter.
  1. changing exe path, exe name, and window name had no effect
  2. possibly looking at process info and dll loaded like XSTool?
* Ragnarok can run alongside normal wxstart.exe but will shutdown in few
  seconds if a admin wxstart.exe is running
* gameguard injects dll into wxstart.exe when wxstart.exe is launched as admin
  after ragnarok is running. Maybe change start.pl to have notepad.exe treated
  as wx interface, this requires recompile wxstart.exe to have the start.pl
  changes baked in
  * This might require rename openkore folder name
  * Change NAME in Settings.pm
