import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import google.generativeai as genai
from concurrent.futures import TimeoutError
from functools import partial

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

# Configure the model
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

max_iterations = 3
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        # Convert the synchronous generate_content call to run in a thread
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: model.generate_content(prompt)
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main():
    """Main execution function"""
    global iteration, last_response
    reset_state()  # Reset at the start of main
    
    print("Starting main execution...")
    print("Establishing connection to MCP server...")
    
    # Create a session with the MCP server using stdio_client
    server_params = StdioServerParameters(
        command="python",
        args=["example2.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    async with stdio_client(server_params) as (read, write):
        print("Connection established, creating session...")
        async with ClientSession(read, write) as session:
            print("Session created, initializing...")
            await session.initialize()
            
            # Get the list of available tools
            print("Requesting tool list...")
            tools_result = await session.list_tools()
            tools = tools_result.tools
            print(f"Successfully retrieved {len(tools)} tools")
            
            # Create a system prompt that describes the available tools
            print("Creating system prompt...")
            print(f"Number of tools: {len(tools)}")
            
            tools_description = []
            for i, tool in enumerate(tools):
                try:
                    # Get tool properties
                    params = tool.inputSchema
                    desc = getattr(tool, 'description', 'No description available')
                    name = getattr(tool, 'name', f'tool_{i}')
                    
                    # Format the input schema in a more readable way
                    if 'properties' in params:
                        param_details = []
                        for param_name, param_info in params['properties'].items():
                            param_type = param_info.get('type', 'unknown')
                            param_details.append(f"{param_name}: {param_type}")
                        params_str = ', '.join(param_details)
                    else:
                        params_str = 'no parameters'

                    tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                    tools_description.append(tool_desc)
                    print(f"Added description for tool: {tool_desc}")
                except Exception as e:
                    print(f"Error processing tool {i}: {e}")
                    tools_description.append(f"{i+1}. Error processing tool")
            
            tools_description = "\n".join(tools_description)
            print("Successfully created tools description")
            
            system_prompt = f"""You are a math agent solving problems in iterations. You have access to various mathematical tools.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...
   
2. For final answers:
   FINAL_ANSWER: [number]

Important:
- When a function returns multiple values, you need to process all of them
- Only give FINAL_ANSWER when you have completed all necessary calculations
- Do not repeat function calls with the same parameters
- For Paint operations, follow this sequence:
  1. First call open_paint to open the application
  2. Wait for Paint to open (about 2 seconds)
  3. Then call draw_rectangle with coordinates (x1,y1,x2,y2)
  4. Wait for the rectangle to be drawn (about 1 second)
  5. Finally call add_text_in_paint with the text to display
- Note: The coordinates are relative to the Paint window's top-left corner
- For single monitor setup, use coordinates within the visible area (e.g., 100,100 to 400,400)

Examples:
- FUNCTION_CALL: add|5|3
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FUNCTION_CALL: open_paint
- FUNCTION_CALL: draw_rectangle|100|100|400|400
- FUNCTION_CALL: add_text_in_paint|Hello World
- FINAL_ANSWER: [42]

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with either FUNCTION_CALL: or FINAL_ANSWER:"""

            # Predefined query for demonstration
            query = """Open Paint, draw a rectangle from (100,100) to (400,400), and add the text 'Hello World' inside it."""
            print("Starting iteration loop...")
            
            while iteration < max_iterations:
                print(f"\n--- Iteration {iteration + 1} ---")
                
                # Handle query based on iteration state
                if last_response is None:
                    current_query = query
                else:
                    current_query = current_query + "\n\n" + " ".join(iteration_response)
                    current_query = current_query + "  What should I do next?"
                
                # Prepare the prompt for the LLM
                print("Preparing to generate LLM response...")
                try:
                    # Generate LLM response
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                        
                        # Find the FUNCTION_CALL line in the response
                        for line in response_text.split('\n'):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:"):
                                response_text = line
                                break
                        
                        if response_text.startswith("FUNCTION_CALL:"):
                            _, function_info = response_text.split(":", 1)
                            parts = [p.strip() for p in function_info.split("|")]
                            func_name, params = parts[0], parts[1:]
                            
                            print(f"\nDEBUG: Raw function info: {function_info}")
                            print(f"DEBUG: Split parts: {parts}")
                            print(f"DEBUG: Function name: {func_name}")
                            print(f"DEBUG: Raw parameters: {params}")
                            
                            # Find the matching tool to get its input schema
                            tool = next((t for t in tools if t.name == func_name), None)
                            if not tool:
                                print(f"DEBUG: Available tools: {[t.name for t in tools]}")
                                raise ValueError(f"Unknown tool: {func_name}")

                            print(f"DEBUG: Found tool: {tool.name}")
                            print(f"DEBUG: Tool schema: {tool.inputSchema}")

                            # Prepare arguments according to the tool's input schema
                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})
                            print(f"DEBUG: Schema properties: {schema_properties}")

                            for param_name, param_info in schema_properties.items():
                                if not params:  # Check if we have enough parameters
                                    raise ValueError(f"Not enough parameters provided for {func_name}")
                                    
                                value = params.pop(0)  # Get and remove the first parameter
                                param_type = param_info.get('type', 'string')
                                
                                print(f"DEBUG: Converting parameter {param_name} with value {value} to type {param_type}")
                                
                                # Convert the value to the correct type based on the schema
                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    # Handle array input
                                    if isinstance(value, str):
                                        value = value.strip('[]').split(',')
                                    arguments[param_name] = [int(x.strip()) for x in value]
                                else:
                                    arguments[param_name] = str(value)

                            print(f"DEBUG: Final arguments: {arguments}")
                            print(f"DEBUG: Calling tool {func_name}")
                            
                            # Add delay for Paint operations
                            if func_name == 'open_paint':
                                print("Waiting for Paint to open...")
                                await asyncio.sleep(2)  # Wait for Paint to open
                            elif func_name == 'draw_rectangle':
                                print("Waiting for rectangle to be drawn...")
                                await asyncio.sleep(1)  # Wait for rectangle to be drawn
                            
                            result = await session.call_tool(func_name, arguments=arguments)
                            print(f"DEBUG: Raw result: {result}")
                            
                            # Get the full result content
                            if hasattr(result, 'content'):
                                print(f"DEBUG: Result has content attribute")
                                # Handle multiple content items
                                if isinstance(result.content, list):
                                    iteration_result = [
                                        item.text if hasattr(item, 'text') else str(item)
                                        for item in result.content
                                    ]
                                else:
                                    iteration_result = str(result.content)
                            else:
                                print(f"DEBUG: Result has no content attribute")
                                iteration_result = str(result)
                                
                            print(f"DEBUG: Final iteration result: {iteration_result}")
                            
                            # Format the response based on result type
                            if isinstance(iteration_result, list):
                                iteration_response = [str(x) for x in iteration_result]
                            else:
                                iteration_response = [str(iteration_result)]
                                
                            last_response = iteration_result
                            print(f"Tool execution result: {iteration_result}")
                            
                        elif response_text.startswith("FINAL_ANSWER:"):
                            print(f"Final answer: {response_text}")
                            break
                            
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        continue
                        
                except Exception as e:
                    print(f"Error in main loop: {e}")
                    continue
                    
                iteration += 1

    print("\nSession closed. Goodbye!")

if __name__ == "__main__":
    asyncio.run(main()) 