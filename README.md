**# NeighbourManager-Networking**
This Python script, a 3rd-year college project, implements a NeighbourManager to manage neighbors and calculate ETX (Expected Transmission Count) metrics in a simulated network. Using multithreading, locks, and timers, it dynamically manages neighbors, probes for updates, selects optimal parents, and logs results. Ideal for IoT and mesh networks.



.................
Long Description:
.................
This Python script implements a NeighbourManager class for managing neighbors and calculating ETX (Expected Transmission Count) metrics in a simulated network. 
The code uses multithreading, locks, and timers to maintain thread-safe operations and periodic tasks.


**Key Techniques and Features:**

...........................
Neighbour Table Management:
...........................
Adds, updates, and removes neighbors dynamically.
Tracks metrics like distance, rank, and TX cost for each neighbor.
Automatically removes inactive neighbors after a 15-second timeout.

...........................
Probing and Acknowledgment:
...........................
Periodically sends PROBE messages to neighbors in a round-robin manner.
Handles PROBE_ACK responses to update link metrics.

................
ETX Calculation:
................
Calculates and updates ETX distance using a weighted average formula based on successful probes.

.............................
Parent Selection and Ranking:
.............................
Identifies the best parent based on the lowest ETX and updates the node's rank accordingly.

..............
Thread Safety:
..............
Uses a lock to ensure safe concurrent access to shared data structures.
Implements timers for periodic probing and retry mechanisms.

......................
Logging and Debugging:
......................
Provides timestamped logs for operations.
Prints the neighbor table periodically for monitoring.
This system is useful for simulating wireless networks, IoT mesh networks, or ad-hoc routing protocols that rely on link quality for efficient communication




