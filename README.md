## Diverged from upstream
* ~~Commented out processGetPlayerInfo() in CoreLogic.pm~~
* Auto char select in xkore
* attackAuto 0 triggers attack with more than 5 monster
* pickup distance increase to 8

## Notes
* processItemsAutoGather is broken and introduced random walk after kill
* increased distance check in processItemsTake so we don't miss any items too
  far away from us
*

* Set TCPNoDelay and TCPAckFrequency registry to 1
* Run XKore 1 on a differnt machine (change listen on 0.0.0.0).
  1. Guest can access host using adapter ip. It's better than the next two methods.
  2. XKore server binds to 0.0.0.0 under NAT and port forwarding,
  3. XKore server binds to 0.0.0.0 under briged and NetRedirect.dll points to virtual machine ip

* Using patched MinHook withouth virtualprotect success check

