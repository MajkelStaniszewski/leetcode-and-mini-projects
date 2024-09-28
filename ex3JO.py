import xml.etree.ElementTree as ET
from datetime import datetime

# Provided PetriNet class with the requested method addition
class PetriNet:

    def __init__(self):
        self.places = {}  # Store places with their token count
        self.transitions = {}  # Store transitions with their names and input/output places

    def add_place(self, place_id):
        """Add a place with the given ID if it doesn't exist"""
        self.places.setdefault(place_id, 0)

    def add_transition(self, name, transition_id):
        """Add a transition with the given name and ID"""
        if transition_id not in self.transitions:
            self.transitions[transition_id] = {
                "name": name,
                "inputs": [],
                "outputs": []
            }

    def add_edge(self, source, target):
        """Create an edge between a place and transition, or vice versa"""
        if source >= 1 and target < 0:  # Place to Transition
            self.transitions[target]["inputs"].append(source)
        elif source < 0 and target >= 1:  # Transition to Place
            self.transitions[source]["outputs"].append(target)
        else:
            raise ValueError(f"Invalid edge from {source} to {target}")
        return self

    def add_marking(self, place_id):
        """Add a token to the specified place"""
        if place_id in self.places:
            self.places[place_id] += 1

    def get_tokens(self, place_id):
        """Return the number of tokens at a place"""
        return self.places.get(place_id, 0)

    def is_enabled(self, transition_id):
        """Check if a transition is enabled (all input places have at least one token)"""
        if transition_id in self.transitions:
            return all(self.places.get(place, 0) > 0 for place in self.transitions[transition_id]["inputs"])
        return False

    def fire_transition(self, transition_id):
        """Fire a transition if it's enabled, moving tokens between places"""
        if self.is_enabled(transition_id):
            # Consume one token from each input place
            for place_id in self.transitions[transition_id]["inputs"]:
                self.places[place_id] -= 1
            # Produce one token at each output place
            for place_id in self.transitions[transition_id]["outputs"]:
                self.places[place_id] += 1

    def transition_name_to_id(self, name):
        """Get transition ID from its name"""
        for t_id, transition in self.transitions.items():
            if transition["name"] == name:
                return t_id
        return None


# Reading XES Log
def read_from_file(file_path):
    """Read an XES file and return a log dictionary with case IDs as keys and event lists as values."""
    log_dict = {}
    tree = ET.parse(file_path)
    root = tree.getroot()
    ns = {'xes': 'http://www.xes-standard.org/'}

    for trace in root.findall('xes:trace', ns):
        case_id = get_case_id(trace, ns)

        if case_id:
            log_dict[case_id] = extract_events(trace, ns)

    return log_dict

def get_case_id(trace, ns):
    """Extract the case ID from a trace element."""
    for attr in trace.findall('xes:string', ns):
        if attr.attrib['key'] == 'concept:name':
            return attr.attrib['value']
    return None

def parse_timestamp(timestamp_str):
    """Helper function to parse the XES timestamp."""
    return datetime.fromisoformat(timestamp_str)

def extract_events(trace, ns):
    """Extract events from a trace element and return them as a list of dictionaries."""
    events = []

    for event in trace.findall('xes:event', ns):
        event_dict = {}

        for attr in event:
            key = attr.attrib['key']

            # Determine the data type based on the tag (e.g., <int>, <string>, <date>, etc.)
            if attr.tag.endswith('int'):
                event_dict[key] = int(attr.attrib['value'])
            elif attr.tag.endswith('string'):
                event_dict[key] = attr.attrib['value']
            elif attr.tag.endswith('date'):
                event_dict[key] = parse_timestamp(attr.attrib['value']).replace(tzinfo=None)
            elif attr.tag.endswith('float'):
                event_dict[key] = float(attr.attrib['value'])
            else:
                event_dict[key] = attr.attrib['value']  # Fallback for other types

        events.append(event_dict)

    return events


# Alpha Miner Algorithm Implementation
def alpha(log):
    T_l = get_unique_events(log)  # Step 1: Define all events
    T_i = get_start_events(log)  # Step 2: Define start events
    T_o = get_end_events(log)    # Step 3: Define end events

    # Step 4: Calculate sets A and B (Causal relation)
    direct_succession, causality, parallelism, no_relation = calculate_relations(log)

    # Discover places based on sets A and B
    places = discover_places(causality, parallelism, no_relation)

    # Step 6-8: Create Petri Net from places and transitions
    petri_net = create_petri_net(T_l, T_i, T_o, places)

    return petri_net


# Supporting Functions for Alpha Miner
def get_unique_events(log):
    """Return all unique events from the log."""
    events = set()
    for events_list in log.values():
        for event in events_list:
            events.add(event["concept:name"])
    return events

def get_start_events(log):
    """Return the starting events (first event in each trace)."""
    start_events = set()
    for events_list in log.values():
        start_events.add(events_list[0]["concept:name"])
    return start_events

def get_end_events(log):
    """Return the ending events (last event in each trace)."""
    end_events = set()
    for events_list in log.values():
        end_events.add(events_list[-1]["concept:name"])
    return end_events

def calculate_relations(log):
    """Calculate direct succession, causality, parallelism, and no relation."""
    direct_succession = set()
    all_events = get_unique_events(log)

    # Collect all direct successions
    for events_list in log.values():
        for i in range(len(events_list) - 1):
            a = events_list[i]["concept:name"]
            b = events_list[i + 1]["concept:name"]
            direct_succession.add((a, b))

    # Initialize relations
    causality = set()
    parallelism = set()

    for a in all_events:
        for b in all_events:
            if (a, b) in direct_succession and (b, a) not in direct_succession:
                causality.add((a, b))
            elif (a, b) in direct_succession and (b, a) in direct_succession:
                parallelism.add((a, b))
                parallelism.add((b, a))

    # Now define no_relation
    no_relation = set()
    for a in all_events:
        for b in all_events:
            if a != b and (a, b) not in causality and (a, b) not in parallelism and (b, a) not in causality and (b, a) not in parallelism:
                no_relation.add((a, b))

    return direct_succession, causality, parallelism, no_relation

def are_independent(set1, set2, no_relation):
    """Check if all elements in set1 are independent of all elements in set2."""
    return all((a, b) in no_relation for a in set1 for b in set2)

def discover_places(causality, parallelism, no_relation):
    """Discover places by calculating the sets of transitions (A,B)."""
    # Initialize with minimal places
    places = [ (frozenset([a]), frozenset([b])) for (a,b) in causality ]

    # Merge places
    merged = True
    while merged:
        merged = False
        new_places = []
        i = 0
        while i < len(places):
            A1, B1 = places[i]
            j = i + 1
            while j < len(places):
                A2, B2 = places[j]
                merged_place = None
                if A1 == A2 and are_independent(B1, B2, no_relation):
                    # Merge B1 and B2
                    B_merged = B1.union(B2)
                    A_merged = A1
                    merged_place = (A_merged, B_merged)
                elif B1 == B2 and are_independent(A1, A2, no_relation):
                    # Merge A1 and A2
                    A_merged = A1.union(A2)
                    B_merged = B1
                    merged_place = (A_merged, B_merged)
                if merged_place:
                    places.pop(j)
                    places[i] = merged_place
                    merged = True
                else:
                    j += 1
            i += 1
        if merged:
            continue  # Continue merging until no more merges occur
    # Remove non-maximal places
    places = drop_non_maximal_sets(places)
    return places

def drop_non_maximal_sets(places):
    """Drop non-maximal sets (A,B) from the list of places."""
    maximal_places = []
    for A1, B1 in places:
        is_maximal = True
        for A2, B2 in places:
            if (A1, B1) != (A2, B2):
                if A1.issubset(A2) and B1.issubset(B2):
                    is_maximal = False
                    break
        if is_maximal:
            maximal_places.append((A1, B1))
    return maximal_places

def create_petri_net(T_l, T_i, T_o, places):
    """Create Petri net based on discovered places and transitions (events)."""
    petri_net = PetriNet()

    # Initialize counters for place and transition IDs
    place_id_counter = 1  # Positive integers for places
    transition_id_counter = -1  # Negative integers for transitions

    # Mapping for event names (transitions) to transition IDs
    event_to_transition = {}

    # Add transitions
    for t in T_l:
        event_to_transition[t] = transition_id_counter
        petri_net.add_transition(t, transition_id_counter)
        transition_id_counter -= 1

    # Add places and connect transitions
    for A, B in places:
        # Create a place
        place_id = place_id_counter
        petri_net.add_place(place_id)
        place_id_counter += 1

        # Connect transitions in A to the place (Transition -> Place)
        for a in A:
            t_id = event_to_transition[a]
            petri_net.add_edge(t_id, place_id)  # Transition -> Place

        # Connect the place to transitions in B (Place -> Transition)
        for b in B:
            t_id = event_to_transition[b]
            petri_net.add_edge(place_id, t_id)  # Place -> Transition

    # Create start place and connect to start transitions
    start_place_id = place_id_counter
    petri_net.add_place(start_place_id)
    petri_net.add_marking(start_place_id)  # Add initial token
    place_id_counter += 1

    for t in T_i:
        t_id = event_to_transition[t]
        petri_net.add_edge(start_place_id, t_id)  # Place -> Transition

    # Create end place and connect from end transitions
    end_place_id = place_id_counter
    petri_net.add_place(end_place_id)
    place_id_counter += 1

    for t in T_o:
        t_id = event_to_transition[t]
        petri_net.add_edge(t_id, end_place_id)  # Transition -> Place

    return petri_net
