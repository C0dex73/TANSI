# Made by CODEX
#~ dependencies
from config import configList as cfg
from typing import overload


#~ classes
class Node :
    """This class representes a node in the network"""

    def __init__(self, _name:str):
        """This function initializes a node object

        Args:
            _name (str): The name of this node
        """
        
        #set class variables
        self.name:str = _name
        self.links:list[Link] = []
        
        
    def __str__(self):
        """This function create the string printed when printing an object of this class"""
        string = "Node :\r\n\t-name : " + self.name + "\r\n\t-links : ["
        for link in self.links:
            string += "\r\n\t\t" + str(link) + ","
        return string.removesuffix(',') + "\r\n\t]"
        
    def addLink(self, _link):
        """This function adds a link to this Node instance

        Args:
            _link (Link): The link object to add
        """
        self.links.append(_link)
    
    
    
    def tick(self) -> list:
        """decreases the weight of links until they are to 0 then return the bound node

        Returns:
            list[Node]: The list of the nodes to tick next time
        """
        
        nodes = []
        for link in self.links :
            link.weight -= 1
            if link.weight == 0:
                nodes.append(link)
            
        
        
class Link : 
    """This class represents a link in the network"""

    def __init__(self, _nodes:list[Node], _weigth:int, _raw:tuple[str, int, str]):
        """This function initializes a link object

        Args:
            _nodes (Node[2]): The two nodes bound by this link
            _weight (int): The weight of the node, a greater weight means that it takes longer to pass through the link
            _raw (tuple[str, int, str]): The link as it is in the config file
        """
        
        #set class variables
        self.nodes:list[Node] = _nodes
        self.weight:int = _weigth
        self.raw:str = str(_raw)
        
        #add this link to the bound nodes
        self.nodes[0].addLink(self)
        self.nodes[1].addLink(self)
        
    def __str__(self):
        """This function create the string printed when printing an object of this class"""
        return str(self.raw)
    
    
    def cross(self, none:Node) -> Node:
        pass


class Network :
    def __init__(self) :
        """The network class contains all the components of the program.\r\n
        It also provides functions to process them
        At initialization all components of the network are created
        """
        self.nodes:list[Node] = []
        self.links:list[Link] = []
        
        #extract config file into the variables
        for link in cfg:
            self.links.append(self.processLink(link))

    def pullNode(self, name) -> Node:
        """Return the corresponding node and create a new if it doesn't exist

        Args:
            name (str) : The name of the node

        Returns:
            Node: The pulled node
        """
        
        for node in self.nodes:
            if node.name == name : return node
        newNode = Node(name)
        self.nodes.append(newNode)
        return newNode


    def processLink(self, link:tuple[str, int, str]) -> Link:
        """Transform the config Link from a tuple to an object

        Args:
            link (tuple[str, int, str]): The config tuple representing the link

        Returns:
            Link: the link processed in an object
        """
        
        #get the Nodes of the link
        lNodes = [self.pullNode(link[0]), self.pullNode(link[2])]
        
        #add link
        return Link(lNodes, link[1], link)

    #overload with string arguments for the IDEs
    @overload
    def shortestPath(self, nodeA:str, nodeB:str) -> list[Node] :
        """Find the shortest path between two nodes.\r\nSlower than shortestPath(self, nodeA:Node, nodeB:Node) -> list[Node] :.

        Args:
            nodeA (str) and nodeB (str): The two nodes to bind

        Returns:
            list[Node]: the nodes that form the path
        """

    def shortestPath(self, nodeA:Node, nodeB:Node) -> list[Node] :
        """Find the shortest path between two nodes

        Args:
            nodeA (Node) and nodeB (Node): The two nodes to bind

        Returns:
            list[Node]: the nodes that form the path
        """
        
        #check for same value or different type
        if nodeA == nodeB : return [nodeA]
        if type(nodeA) != type(nodeB) : raise TypeError("Expected nodeA and nodeB to be the same type")
        
        #if inputed as their name, find the nodes
        if(type(nodeA) == str):
            for node in self.nodes :
                if node.name == nodeA : nodeA = node
                if node.name == nodeB : nodeB = node
        #handle wrong type arguments
        elif type(nodeA) != Node : raise TypeError("Expected nodeA and nodeB to be string or Node objects")
        
        
    

#* main program
def main():
    """The main function called at the start of the program"""
    
    network = Network()
    network.shortestPath(network.nodes[2], "A")

#* EXECUTE

if(__name__ == '__main__'):
    main()