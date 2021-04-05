#################Functions used by program bgp_netconf_configure.py#################
def format_namespace(ns,tree_element):
    '''
    format_namespace function is used to concatenate namespace to xml element
    :param ns: Namespace for the xml element
    :param tree_element: xml element
    :return string formatted in the format {namespace}elementname:
    '''
    ns = "{" + ns + "}"
    return_string=ns+tree_element
    return(return_string)

def convert_to_config(input_str):
    '''
    convert_to_config converts the xml received during data retrieval to config format
    :param input_str: XML string received during data retrieval
    :return: XML string modified to configure network element
    '''
    return(input_str.replace('ns0:data','ns0:config'))

def get_bgp_router_filter(native_ns,ns):
    '''
    get_bgp_router_filter is used to retrieve bgp configuration
    :param native_ns: Native namespace
    :param ns: BGP namespace
    :return: Filter to retrieve bgp configuration
    '''
    return_string = """
  <filter>
      <native xmlns="%s">
        <router>
          <bgp xmlns="%s">
          </bgp>
        </router>
      </native>
  </filter>
""" % (native_ns,ns)
    return return_string


def get_bgp_state_filter(ns):
    '''
    get_bgp_state_filter is used to retrieve bgp neighbors operation state
    :param ns: BGP namespace for operation state
    :return: Filter to retrieve bgp neighbors operation state
    '''
    return_string =  """
 <filter>
          <bgp-state-data xmlns="%s">
          <neighbors><neighbor></neighbor></neighbor>
          </bgp-state-data>
  </filter>
""" % (ns)
    return return_string

def iterate_xml(xml_node,lookup_info,tree_traversal_flag=1):
    '''
    iterate_xml is used to iterate through the xml and make changes
    as per the input json file
    :param xml_node: xml root
    :param lookup_info: json data file
    :return: returns true if successful tree traversal
    '''
    for child in xml_node:
        lookup_key = child.tag.split('}')[1]
        if lookup_key in lookup_info:
            if type(lookup_info[lookup_key])==dict:
                iterate_xml(child,lookup_info[lookup_key] )
            else:
                child.text = lookup_info[lookup_key]
    if tree_traversal_flag:
        return (True)
    else:
        return (False)

def get_bgp_neighbor_state(bgp_state_details,node_ip):
    '''
    get_bgp_neighbor_state functions get the bgp neighbor state.
    :param bgp_state_details: Output from retrieval of bgp neighbor state
    :param node_ip: neighbor to check for connection status
    :return: returns connection state or False if neighbor not found.
    '''
    bgp_neighbor_info=bgp_state_details["rpc-reply"]["data"]['bgp-state-data']['neighbors']['neighbor']
    for bgp_neighbor in bgp_neighbor_info:
        if bgp_neighbor['neighbor-id']==node_ip:
            return bgp_neighbor['connection']['state']
    return(False)
