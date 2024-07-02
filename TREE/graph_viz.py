import os
from bs4 import BeautifulSoup
from graphviz import Digraph

def visualize_xml_hierarchy(xml_folder):
    # Initialize a directed graph
    dot = Digraph(comment='TEI XML Hierarchy')

    # Set to keep track of already added connections
    connections_set = set()

    # Iterate through each XML file in the folder
    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            file_path = os.path.join(xml_folder, filename)

            # Parse the XML file using BeautifulSoup
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'xml')

            # Traverse the XML tree and add edges to the graph
            traverse_xml_tree(dot, soup.body, None, connections_set)

    # Save the graph as a PNG file
    dot.render('tei_xml_hierarchy', format='png', cleanup=True)

def traverse_xml_tree(graph, element, parent_tag, connections_set):
    # Add the current tag to the graph
    current_tag = element.name
    graph.node(current_tag)

    # Add an edge to connect the current tag with its parent if not already added
    if parent_tag is not None and (parent_tag, current_tag) not in connections_set:
        graph.edge(parent_tag, current_tag)
        connections_set.add((parent_tag, current_tag))

    # Recursively traverse the child elements
    for child in element.children:
        if child.name is not None:
            traverse_xml_tree(graph, child, current_tag, connections_set)

if __name__ == "__main__":
    # Specify the folder containing TEI XML files
    xml_folder = '/home/pg/Documents/GitHub/Babits_lira/BABITS 4'

    # Visualize the XML hierarchy
    visualize_xml_hierarchy(xml_folder)
