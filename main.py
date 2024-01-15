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
            #* used + "" and .copy() to separate the new backup from his original version
            self.name:str = originalNode.name + ""
            self.links:list[Link] = originalNode.links.copy()
            self.trace:list = originalNode.trace.copy()
            self.pathWeight:int = originalNode.pathWeight
        else:
            self.name:str = _name
            self.links:list[Link] = []
            self.trace:list = []
            self.pathWeight:int = 0
            self.backup = Node("", self)
    
    def __str__(self):
        """This function create the string printed when printing an object of this class"""
        
        string = "Node :\r\n\t-name : " + self.name + "\r\n\t-links : ["
        for link in self.links:
            string += "\r\n\t\t" + str(link) + "[" + str(link.weight )+"]" + ","
        string = string.removesuffix(',') + "\r\n\t]\r\n\t-tracePile : ["
        for node in self.trace:
            string += node.name + ","
        return string.removesuffix(',') + "]\r\n\t-pathWeight : " + str(self.pathWeight)
    
    def getBackup(self):
        """Returns a backup of this class from the initialization of the network

        Returns:
            Node: The node's backup
        """
        return Node("", self.backup)
    
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

    def tick(self, useLinksBackup:bool=False, useNodeBackup:bool=False) -> list:
        """decreases the weight of links until they are to 0 then return the bound node

        Returns:
            list[Node]: The list of the nodes to tick next time
        """
        
        #list the new nodes reached by the algorithm
        nodes:list[Node|None] = []
        i:int = 0
        while i < len(self.links):
            link = self.links[i]
            #if the link is already crossed use his backup
            if link.crossed and useLinksBackup: link = link.getBackup()
            #if we are crossing it, fetch the next node
            if(link.tick()):
                #substract one to add one instead of 0at the en of the iteration
                i -= 1
                nodes.append(link.cross(self, useNodeBackup))
                if nodes[len(nodes)-1] is None : nodes.pop() #In case it's a dead-end
            i += 1
        if len(self.links) != 0 : nodes.append(self)
        return nodes

    def traceBack(self, showWeight:bool=True, withSelf:bool=True) -> list[str]:
        """Trace back the path used to get to this node from the root node

        Args:
            withSelf (bool, optional): Return the path with this node at the end. Defaults to True.
            showWeight (bool, optional): Return the path with the total weight that the path took from the root node to this one\r\nas a string as last element of the list.

        Returns:
            list[str]: The path, list of the name of the nodes
        """
        path = [node.name for node in self.trace]
        if withSelf : path.append(self.name)
        if showWeight : path.append(str(self.pathWeight))
        return path


class Link : 
    """This class represents a link in the network"""

    def __init__(self, _nodes:list[Node], _weight:int, _raw:tuple[str, int, str], originalLink=None):
        """This function initializes a link object

        Args:
            _nodes (Node[2]): The two nodes bound by this link
            _weight (int): The weight of the node, a greater weight means that it takes longer to pass through the link
            _raw (tuple[str, int, str]): The link as it is in the config file
            originalLink (Link|None, optional): the link to copy in case of backup (let Nonde if it is not a backup) (same mecanic as Node's backups)
        """
        
        self.isBackup = originalLink is not None
        self.crossed = False
        if(self.isBackup):
            #set class variables
            self.nodes:list[Node] = originalLink.nodes
            self.weight:int = originalLink.weight
            self.raw:tuple[str, int, str] = originalLink.raw
        else:
            #set class variables
            self.nodes:list[Node] = _nodes
            self.weight:int = _weight
            self.raw:tuple[str, int, str] = _raw
            
            #add this link to the bound nodes
            self.nodes[0].addLink(self, True)
            self.nodes[1].addLink(self, True)

            #init backup
            self.backup = Link(None, None, None, self)
        
        
    
    def __str__(self):
        """This function create the string printed when printing an object of this class"""
        return str(self.raw)
    
    def cross(self, node:Node, useBackup:bool=False) -> Node:
        """Return the other node of the link than the node inputed in argument

        Args:
            node (Node): The node that want to cross the link
            useBackup (bool, optional): If the other node is or was already processed from another path\r\nuse it's backup to have a fresh node like at initialization.\r\nDefaults to False.

        Returns:
            Node: The node from the other side
        """
        #get the other node
        if node == self.nodes[0] : target = self.nodes[1]
        else : target = self.nodes[0]
        #avoid looping
        if node.trace.__contains__(target) : return None
        #chose whether or not to use backup if node already processed
        if(len(target.trace) != 0):
            if not useBackup : return None
            target = target.getBackup()
        #return the node and set its tracing system according to the one of the current node.
        target.trace = node.trace.copy()
        target.trace.append(node)
        target.pathWeight = node.pathWeight + self.raw[1]
        return target
    
    def tick(self) -> bool:
        """decrease the weight, if it is ready to be crossed (weight==0) then remove it from its nodes\r\n(both to avoid goings and comings along a single link)

        Returns:
            bool: whether or not it is ready to be crossed
        """
        self.weight -= 1
        if self.weight > 0 : return False
        for node in self.nodes : node.removeLink(self)
        self.crossed = True
        return True
    
    
    def getBackup(self):
        """Returns a backup of this class from the initialization of the network

        Returns:
            Link: The link's backup
        """
        return Link(None, None, None, self.backup)



class Network :
    """This class represents the network itself and provides memthods to operate it"""
    
    def __init__(self) :
        """The network class contains all the components of the program.\r\n
        It also provides functions to process them
        At initialization all components of the network are created
        """
        self.nodes:list[Node] = []
        self.links:list[Link] = []
        
        #setup the root node, used to avoid going back and forth between the first node and a second one when pathfinding
        self.root = Node("root")
        
        #extract config file into the variables
        for link in cfg:
            self.links.append(self.processLink(link))

    def reset(self):
        """Resets the network class, call __init__ function"""
        self.__init__()

    def pullNode(self, name) -> Node:
        """Return the corresponding node and create a new if it doesn't exist

        Args:
            name (str) : The name of the node

        Returns:
            Node: The pulled node
        """
        #if it already exists return it as node object
        for node in self.nodes:
            if node.name == name : return node
        #otherwise create it and return it
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
        
        #get the nodes into node type objects
        nodeA, nodeB = self.formatNodes(nodeA, nodeB)

        #tag nodeA as root
        nodeA.trace = [self.root]
        
        # list of the nodes processed in the current tick
        toTick:list[Node] = [nodeA]
        # list of the nodes to process in the following tick
        nextTT:list[Node] = []
        
        #~ main loop
        while nodeB not in toTick:
            #!debug(toTick)
            for node in toTick:
                nextTT.extend(node.tick())
            #remove duplicates and assign the nodes to be processed in the next iteration
            toTick = list(set(nextTT))
            #!debug(toTick)
        
        return(nodeB.traceBack())
    
    #overload with string arguments for the IDEs
    @overload
    def longestPath(self, nodeA:str, nodeB:str) -> list[Node] :
        """Find the longest path between two nodes.\r\nSlower than longestPath(self, nodeA:Node, nodeB:Node) -> list[Node] :.

        Args:
            nodeA (str) and nodeB (str): The two nodes to bind

        Returns:
            list[Node]: the nodes that form the path
        """
    
    def longestPath(self, nodeA:Node, nodeB:Node) -> list[Node]:
        """Find the longest path between two nodes

        Args:
            nodeA (Node) and nodeB (Node): The two nodes to bind

        Returns:
            list[Node]: the nodes that form the path
        """
        #check for same value or different type
        if nodeA == nodeB : return [nodeA]
        
        #get the nodes into node type objects
        nodeA, nodeB = self.formatNodes(nodeA, nodeB)
        
        #tag nodeA as root
        nodeA.trace = [self.root]
        
        # list of the nodes processed in the current tick
        toTick:list[Node] = [nodeA]
        # list of the nodes to process in the following tick
        nextTT:list[Node] = []
        
        finalResult:list[str] = []
        
        #~ main loop
        while len(toTick) > 0:
            #!debug(toTick, "tT")
            for node in toTick:
                nextTT.extend(node.tick(useNodeBackup=True))
            #remove duplicates and assign the nodes to be processed in the next iteration
            #!debug(nextTT, "TT")
            for node in nextTT:
                #if the name matches (could be bakckups and names are unique)
                if(node.name == nodeB.name):
                    nextTT.remove(node)
                    traceBack = node.traceBack()
                    #safe parse
                    try:
                        #compare path weight
                        if(int(traceBack[len(traceBack)-1]) > (int(finalResult[len(finalResult)-1])if len(finalResult) > 0 else 0)):
                            finalResult = traceBack
                    except Exception as e:
                        print("Oops, an error occurred while parsing the path weight : " + str(e))
                    
                    
            #init toTick for next iteration and empty nextTT
            toTick = list(set(nextTT))
            nextTT = []
        return finalResult
    
    def formatNodes(self, nodeA:Node, nodeB:Node) -> tuple[Node, Node]:
        """Format a two nodes as two nodes or two strings into their respective node objects

        Args:
            nodeA (Node): the first node to parse
            nodeB (Node): the second one

        Raises:
            TypeError: Raised when node a and b arn't the same type
            TypeError: Raised when node a or b arn't string or node

        Returns:
            tuple[Node, Node]: the two nodes as node objects
        """
        if type(nodeA) != type(nodeB) : raise TypeError("Expected nodeA and nodeB to be the same type.\r\nnodeA : " + str(type(nodeA)) + " and nodeB : " + str(type(nodeB)))
        
        #if inputed as their name, find the nodes
        if(type(nodeA) == str):
            for node in self.nodes :
                if node.name == nodeA : nodeA = node
                if node.name == nodeB : nodeB = node
        #handle wrong type arguments
        elif type(nodeA) != Node : raise TypeError("Expected nodeA and nodeB to be string or Node objects.\r\nThey are " + str(type(nodeA)))
        return nodeA, nodeB
        

def debug(list:list[Node], calledFrom:str=""):
    """used while debugging the project, shows a list of nodes as their own string representations

    Args:
        list (list[Node]): The list of node to display
        calledFrom (str, optional): Shows in the console an optional message to say where it was called from. Defaults to "".
    """
    print(("#debug from " + calledFrom) if calledFrom!="" else "#debug")
    for node in list:
        print(str(node))
    input()

#* main program
def main():
    """The main function called at the start of the program"""
    #initialize the network
    network = Network()
    
    #search for the shortest path between nodes "A" and "C"
    print(network.shortestPath("A", "C"))
    
    #reset network
    network.reset()
    
    #search for the longest path between nodes "A" and "C"
    print(network.longestPath("A", "C"))

#* EXECUTE
if(__name__ == '__main__'):
    main()