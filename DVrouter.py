from router import Router
from packet import Packet
import json

INFINITY = 16

class DVrouter(Router):
    def __init__(self, addr, heartbeat_time):
        Router.__init__(self, addr)
        self.heartbeat_time = heartbeat_time
        self.last_time = 0

        # dest -> (cost, port)
        self.routing_table = {} 
        
        # port -> cost
        self.link_costs = {} 
        
        # port -> neighbor
        self.port_to_neighbor = {} 
        
        # neighbor -> port
        self.neighbor_to_port = {}  
        
        # dest -> neighbor
        self.via = {}
        
        # neighbor -> {dest: cost}
        self.neighbor_dvs = {}   

        self.routing_table[self.addr] = (0, None)
        self.via[self.addr] = self.addr

    def send_dv_to_neighbors(self):
        for neighbor_addr, port in self.neighbor_to_port.items():
        
            # dest -> cost
            poisoned_dv = {}
            
            for dest, (cost, next_hop) in self.routing_table.items():
                # Poison reverse: nếu học route này từ neighbor, gửi cost = INFINITY
                if next_hop == port:
                    poisoned_dv[dest] = INFINITY
                else:
                    poisoned_dv[dest] = cost
            content = json.dumps(poisoned_dv)
            packet = Packet(Packet.ROUTING, self.addr, neighbor_addr, content)
            self.send(port, packet)

    def update_routing_table(self):
        changed = False
        new_table = {self.addr: (0, None)}  # Luôn giữ route đến chính mình
        new_via = {self.addr: self.addr}

        all_dests = set()
        for dv in self.neighbor_dvs.values():
            all_dests.update(dv.keys())
        all_dests.update(self.routing_table.keys())
        all_dests.update(self.via.keys())
        all_dests.update(self.neighbor_to_port.keys())
        all_dests.discard(self.addr)

        for dest in all_dests:
            best_cost = INFINITY
            best_port = None
            best_via = None

            for neighbor, port in self.neighbor_to_port.items():
                cost_to_neighbor = self.link_costs.get(port, INFINITY)
                neighbor_dv = self.neighbor_dvs.get(neighbor, {})
                cost_from_neighbor = neighbor_dv.get(dest, INFINITY)
                total_cost = min(INFINITY, cost_to_neighbor + cost_from_neighbor)

                if total_cost < best_cost:
                    best_cost = total_cost
                    best_port = port
                    best_via = neighbor

            # Nếu có link trực tiếp đến dest
            if dest in self.neighbor_to_port:
                port = self.neighbor_to_port[dest]
                direct_cost = self.link_costs.get(port, INFINITY)
                if direct_cost < best_cost:
                    best_cost = direct_cost
                    best_port = port
                    best_via = dest

            if best_cost < INFINITY:
                new_table[dest] = (best_cost, best_port)
                new_via[dest] = best_via

        if new_table != self.routing_table:
            self.routing_table = new_table
            self.via = new_via
            changed = True

        return changed

    def handle_packet(self, port, packet):
        if packet.is_traceroute:
            dest = packet.dst_addr
            if dest in self.routing_table:
                next_port = self.routing_table[dest][1]
                self.send(next_port, packet)
        else:
            neighbor = packet.src_addr
            dv = json.loads(packet.content)
            self.neighbor_dvs[neighbor] = dv

            if self.update_routing_table():
                self.send_dv_to_neighbors()

    def handle_new_link(self, port, endpoint, cost):
        self.link_costs[port] = cost
        self.port_to_neighbor[port] = endpoint
        self.neighbor_to_port[endpoint] = port
        self.neighbor_dvs[endpoint] = {}

        # Thêm route trực tiếp đến neighbor nếu cần
        self.routing_table[endpoint] = (cost, port)
        self.via[endpoint] = endpoint

        if self.update_routing_table():
            self.send_dv_to_neighbors()
        else:
            self.send_dv_to_neighbors()

    def handle_remove_link(self, port):
        neighbor = self.port_to_neighbor.get(port)

        if neighbor:
            self.neighbor_dvs.pop(neighbor, None)
            self.neighbor_to_port.pop(neighbor, None)

        self.link_costs.pop(port, None)
        self.port_to_neighbor.pop(port, None)

        # Xóa các route đi qua port bị mất
        routes_to_remove = [dst for dst, (_, p) in self.routing_table.items() if p == port]
        for dst in routes_to_remove:
            self.routing_table.pop(dst, None)
            self.via.pop(dst, None)

        if self.update_routing_table():
            self.send_dv_to_neighbors()
        else:
            self.send_dv_to_neighbors()

    def handle_time(self, time_ms):
        if time_ms - self.last_time >= self.heartbeat_time:
            self.last_time = time_ms
            self.send_dv_to_neighbors()

    def __repr__(self):
        lines = [f"Routing Table for {self.addr}:"]
        for dest, (cost, port) in sorted(self.routing_table.items()):
            lines.append(f"  {dest}: cost {cost}, port {port}")
        return "\n".join(lines)