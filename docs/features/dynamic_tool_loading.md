# Dynamic Tool Loading

Semantic Kernel provides the `as_mcp_server` function to expose any Pluins and their corresponding tools as MCP tools.

However, there are some out of box limitations around how Semantic Kernel exposes the plugin functions. For example:

- When adding mulitple versions of a tool, functions with the same name will overwrite each other.

Obviously this is not ideal.  So the GPT-RAG-MCP MCP Server gets around this by allow for a `prefix` and `suffix` as part of the tool settings.

In the `base_plugin.py`, notice the following `reset_kernel_functions` method:

```python
def reset_kernel_functions(self, settings : Dict = {}):
    for name, oldMethod in inspect.getmembers(self, predicate=inspect.ismethod):        
        method = copy.copy(oldMethod)
        
        methodName = method.__name__
        if hasattr(method, '__kernel_function_description__'):
            methodDescription = method.__getattribute__('__kernel_function_description__')
            method.__func__.__setattr__('__kernel_function_description__', settings.get(f"{methodName}_description", methodDescription))

        if hasattr(method, '__kernel_function_name__'):
            methodDescription = method.__getattribute__('__kernel_function_name__')
            method.__func__.__setattr__('__kernel_function_name__', f"{self.prefix}{methodName}{self.suffix}")
            setattr(self, f"{self.prefix}{methodName}{self.suffix}", method)
```

This code will rename the `kernel_function` added attributes of the method to utilize the `prefix` or `suffix` if it has been passed in.

This occurs as part of class instantation, before it is loaded into the semantic kernel.  This allows you to have multiple versions of the same plugin tools, with custom descriptions for each.

Common patterns for this include the Azure Blob Tool.  If you want the LLM to interact with three different containers (ex `bronze`, `silver`, `gold`), you will need three different instances of the tool with descriptions that tell the LLM when they should use each instance.