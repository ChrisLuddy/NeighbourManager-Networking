#cs3
#Christopher Luddy



#imports
import threading
import time
import random
import datetime

def log(message):
    """Helper function for timestamped debug logs."""
    print(f"[{datetime.datetime.now()}] {message}")

class NeighbourManager:
    """NeighbourManager Class for managing neighbours and ETX metrics."""
    def __init__(self):
        self.neighbour_table = {}  # Dictionary to store neighbour state
        self.lock = threading.Lock()  # Lock for thread safety
        self.probe_interval = 5  # Base interval for probing in seconds
        self.current_neighbour = None  # Track the neighbour being probed
        self.stop_probing = False  # Control flag to stop probing
        self.rank = 999  # Initialize the node rank to infinity
        self.potential_parents = {}  # Dictionary of potential parents

    def add_or_update_neighbour(self, node_id):
        """Adds or updates a neighbour's state, including resetting the timeout timer."""
        with self.lock:
            if node_id in self.neighbour_table:
                log(f"Updating neighbour {node_id}")
                self.neighbour_table[node_id]['timeout_timer'].cancel()
            else:
                log(f"Adding new neighbour {node_id}")
                self.neighbour_table[node_id] = {
                    'distance': 1,  # Start at a distance of 1
                    'rank': None,
                    'timeout_timer': None,
                    'resend_timer': None,
                    'tx_cost': 0
                }

            # Set or reset the timeout timer to 15 seconds
            timer = threading.Timer(15, self.remove_neighbour, args=[node_id])
            self.neighbour_table[node_id]['timeout_timer'] = timer
            timer.start()

    def remove_neighbour(self, node_id):
        """Removes a neighbour when the timeout timer expires."""
        with self.lock:
            if node_id in self.neighbour_table:
                log(f"Timeout expired: Removing neighbour {node_id}")
                self.neighbour_table[node_id]['timeout_timer'].cancel()
                if self.neighbour_table[node_id]['resend_timer']:
                    self.neighbour_table[node_id]['resend_timer'].cancel()
                del self.neighbour_table[node_id]

                # If this was a potential parent, update the parent list
                if node_id in self.potential_parents:
                    log(f"Removed {node_id} from potential parents due to timeout.")
                    del self.potential_parents[node_id]
                    self.update_parents()
            else:
                log(f"Node {node_id} not found for removal.")

    def probe_neighbours(self):
        """Probes neighbours periodically and calculates ETX."""
        while not self.stop_probing:
            with self.lock:
                if not self.neighbour_table:
                    log("No neighbours to probe.")
                    time.sleep(self.probe_interval)
                    continue

                # Select the next neighbour in sequence
                neighbours = list(self.neighbour_table.keys())
                if self.current_neighbour is None or self.current_neighbour not in self.neighbour_table:
                    self.current_neighbour = neighbours[0]
                else:
                    current_index = neighbours.index(self.current_neighbour)
                    self.current_neighbour = neighbours[(current_index + 1) % len(neighbours)]

                log(f"Probing neighbour: {self.current_neighbour}")

            # Simulate sending a PROBE
            self.send_probe(self.current_neighbour)

            # Wait for the next probe interval with a small random offset
            time.sleep(self.probe_interval + random.uniform(0, 1))

    def send_probe(self, node_id):
        """Simulate sending a PROBE message."""
        with self.lock:
            if node_id not in self.neighbour_table:
                return

            tx_cost = self.neighbour_table[node_id]['tx_cost']
           
            # Prevent retrying if max retries are reached
            if tx_cost >= 5:
                log(f"Max retries reached for {node_id}. Skipping PROBE.")
                return
           
            tx_cost += 1
            self.neighbour_table[node_id]['tx_cost'] = tx_cost
            log(f"Sent PROBE to {node_id}. TX cost: {tx_cost}")

            # Set a resend timer for this neighbour
            resend_timer = threading.Timer(0.5, self.resend_probe, args=[node_id])
            self.neighbour_table[node_id]['resend_timer'] = resend_timer
            resend_timer.start()

    def resend_probe(self, node_id):
        """Resend a PROBE if no ACK is received."""
        with self.lock:
            if node_id in self.neighbour_table:
                # Limit retries to avoid infinite resends
                if self.neighbour_table[node_id]['tx_cost'] >= 5:
                    log(f"Max retries reached for {node_id}. Stopping PROBE resends.")
                    return

                tx_cost = self.neighbour_table[node_id]['tx_cost']
                tx_cost += 1
                self.neighbour_table[node_id]['tx_cost'] = tx_cost
                log(f"Resending PROBE to {node_id}. TX cost: {tx_cost}")

                # Reschedule resend timer
                resend_timer = threading.Timer(0.5, self.resend_probe, args=[node_id])
                self.neighbour_table[node_id]['resend_timer'] = resend_timer
                resend_timer.start()

    def receive_probe_ack(self, node_id):
        """Handle receipt of a PROBE_ACK."""
        with self.lock:
            if node_id in self.neighbour_table:
                # reset timeout timer
                self.add_or_update_neighbour(node_id)
               
                # Cancel the resend timer
                resend_timer = self.neighbour_table[node_id]['resend_timer']
                if resend_timer:
                    resend_timer.cancel()
                    self.neighbour_table[node_id]['resend_timer'] = None # Clear timer reference
                   
                self.neighbour_table[node_id]['tx_cost'] = 0

                # Update the distance using the ETX formula
                old_distance = self.neighbour_table[node_id]['distance']
                new_distance = (old_distance * 0.5) + (1 * 0.5)  # Tx cost of 1 for successful probe
                self.neighbour_table[node_id]['distance'] = new_distance
                log(f"Updated distance for {node_id}: {new_distance}")

                # Check for potential parent update
                self.add_potential_parent(node_id, new_distance)
            else:
                log(f'Recieved PROBE_ACK from unknown node {node_id}. Ignoring.')

    def add_potential_parent(self, node_id, distance):
        """Add or update potential parents based on rank and distance."""
        if node_id not in self.potential_parents or distance < self.potential_parents[node_id]['distance']:
            self.potential_parents[node_id] = {'distance': distance}
            log(f"Added {node_id} to potential parents with distance {distance}")
            self.update_parents()

    def update_parents(self):
        """Update the preferred parent based on potential parents."""
        if not self.potential_parents:
            log("No potential parents available. Setting rank to infinity.")
            self.rank = 999
        else:
            # Select the parent with the smallest distance
            best_parent = min(self.potential_parents, key=lambda node: self.potential_parents[node]['distance'])
            self.rank = self.potential_parents[best_parent]['distance'] + 1
            log(f"Selected {best_parent} as the parent with distance {self.potential_parents[best_parent]['distance']}")

    def stop(self):
        """Stop the probing process."""
        self.stop_probing = True
        with self.lock:
            for node_id, details in self.neighbour_table.items():
                if details['timeout_timer']:
                    details['timeout_timer'].cancel()
                if details['resend_timer']:
                    details['resend_timer'].cancel()

    def print_neighbour_table(self):
        """Print the current neighbour table."""
        with self.lock:
            log("\n--- Current Neighbour Table ---")
            if not self.neighbour_table:
                log("No neighbours present.")
            else:
                for node_id, details in self.neighbour_table.items():
                    log(f"Node {node_id}: Distance = {details['distance']}, TX Cost = {details['tx_cost']}")
            log("--------------------------------\n")

# Testing the Code + debugging
if __name__ == "__main__":
    manager = NeighbourManager()

    # Add 50 nodes dynamically
    for i in range(1, 51):  # Loop from 1 to 50
        node_id = f"Node{i}"  # Generate node ID (Node1, Node2, ..., Node50)
        manager.add_or_update_neighbour(node_id)
        time.sleep(0.1)  # A brief sleep to avoid system crash

    # Print initial state
    manager.print_neighbour_table()

    # Allow a brief delay to ensure the neighbours are fully added
    time.sleep(2)

    # Start probing neighbours
    probe_thread = threading.Thread(target=manager.probe_neighbours)
    probe_thread.start()

    # Simulate receiving PROBE_ACK messages after some time
    time.sleep(3)
    manager.receive_probe_ack("Node1")
    time.sleep(3)
    manager.receive_probe_ack("Node2")

    # Periodically print the table to observe updates
    for _ in range(3):
        time.sleep(5)
        manager.print_neighbour_table()

    # Stop the probing after 20 seconds
    time.sleep(20)

    # Stop the probing and cleanup
    manager.stop()
    probe_thread.join()
    log("Program exited cleanly.")