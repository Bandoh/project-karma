response_schema = {
    "content":" if tool is needed tell me the steps. \n If no tool is needed put response here",
    "tool_call":"true or false. \ndepending on where you need a tool to fulfil request",
    "tool (this shows only if tool_call is true)":{ 
        "tool_name": "specify the specific tool_name i have provided you with",
        "args":"""arguements needed for the tool it should be a map eg. {"command":"ls -la"}"""
    }
    
}