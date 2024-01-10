# Made by CODEX
#~ dependencies
from config import configList as cfg
from typing import overload


#~ classes
class Node :
    """This class representes a node in the network"""

    def __init__(self, _name:str, originalNode=None):
        """This function initializes a node object, or create a copy of another if originalNode is not None

        Args:
            _name (str): The name of this node (ignored if originalNode is not None)
            originalNode (Node): The node to copy if not None. Default to None
        """
        
        #set class variables
        self.isBackup:bool = originalNode is not None
        if(self.isBackup):
            #* used + "" and .copy() to separate the two objects
            self.name:str = originalNode.name + ""
            self.links:list[Link] = originalNode.links.copy()
            self.trace:list = originalNode.trace.copy()
        else:
            self.name:str = _name
            self.links:list[Link] = []
            self.trace:list = []
            self.backup = Node("", self)
    
    def __str__(self):
        """This function create the string printed when printing an object of this class"""
        
        string = "Node :\r\n\t-name : " + self.name + "\r\n\t-links : ["
        for link in self.links:
            string += "\r\n\t\t" + str(link) + "[" + str(link.weight )+"]" + ","
        string = string.removesuffix(',') + "\r\n\t]\r\n\t-tracePile : ["
        for node in self.trace:
            string += node.name + ","
        return string.removesuffix(',') + "]"
    
    def addLink(self, _link, overwriteBackup:bool=False):
        """This function adds a link to this Node instance

        Args:
            _link (Link): The link object to add
            overwriteBackup (bool, optional): Modifies backup node too. Defaults to False.
        """
        
        self.links.append(_link)
        if overwriteBackup and not self.isBackup : self.backup.links.append(_link)
    
    def removeLink(self, _link, overwriteBackup:bool=False):
        """This function removes a link to this Node instance

        Args:
            _link (Link): The link object to remove
            overwriteBackup (bool, optional): Modifies backup node too. Defaults to False.
        """
        
        self.links.remove(_link)
        if overwriteBackup and not self.isBackup: self.backup.links.remove(_link)

    def tick(self) -> list:
        """decreases the weight of links until they are to 0 then return the bound node

        Returns:
            list[Node]: The list of the nodes to tick next time
        """
        #list the new nodes reached by the algorithm
        nodes:list[Node|None] = []
        for link in self.links : 
            #if the link is crossed
            if(link.tick()):
                nodes.append(link.cross(self))
                if nodes[len(nodes)-1] is None : nodes.pop() #In case it's a dead-end
        if len(self.links) != 0 : nodes.append(self)
        return nodes

    def traceBack(self, withSelf=True) -> list[str]:
        """Trace back the path used to get to this node from the root node

        Args:
            withSelf (bool, optional): Return the path with this node at the end. Defaults to True.

        Returns:
            list[str]: The path, list of the name of the nodes
        """
        path = [node.name for node in self.trace]
        if withSelf : path.append(self.name)
        return path


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
        self.nodes[0].addLink(self, True)
        self.nodes[1].addLink(self, True)
    
    def __str__(self):
        """This function create the string printed when printing an object of this class"""
        return str(self.raw)
    
    def cross(self, node:Node, useBackup:bool=False) -> Node:
        if node == self.nodes[0] : target = self.nodes[1]
        else : target = self.nodes[0]
        if len(target.trace) != 0: return [None, target.backup][useBackup]
        target.trace = node.trace.copy()
        target.trace.append(node)
        return target
    
    def tick(self) -> bool:
        self.weight -= 1
        if self.weight > 0 : return False
        for node in self.nodes : node.removeLink(self)
        return True


class Network :
    """This class represents the network itself and provides memthods to operate it"""
    
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
        if type(nodeA) != type(nodeB) : raise TypeError("Expected nodeA and nodeB to be the same type.\r\nnodeA : " + str(type(nodeA)) + " and nodeB : " + str(type(nodeB)))
        
        #if inputed as their name, find the nodes
        if(type(nodeA) == str):
            for node in self.nodes :
                if node.name == nodeA : nodeA = node
                if node.name == nodeB : nodeB = node
        #handle wrong type arguments
        elif type(nodeA) != Node : raise TypeError("Expected nodeA and nodeB to be string or Node objects.\r\nThey are " + str(type(nodeA)))

        # list of the nodes processed in the current tick
        toTick:list[Node] = [nodeA]
        # list of the nodes to process in the following tick
        nextTT:list[Node] = []
        
        #~ main loop
        while nodeB not in toTick:
            for node in toTick:
                nextTT.extend(node.tick())
            #remove duplicates and assign the nodes to be processed in the next iteration
            toTick = list(set(nextTT))
        
        #print result
        print(nodeB.traceBack())

#! DEBUG
def debug(list:list[Node]):
    for node in list:
        print(str(node))
    input()

#* main program
def main():
    """The main function called at the start of the program"""
    
    network = Network()
    network.shortestPath("A", "G")

#* EXECUTE
if(__name__ == '__main__'):
    main()