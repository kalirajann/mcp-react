# basic import 
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.fastmcp.prompts import base
from mcp.types import TextContent
from mcp import types
from PIL import Image as PILImage
import math
import sys
from pywinauto.application import Application
import win32gui
import win32con
import time
from win32api import GetSystemMetrics

# instantiate an MCP server client
mcp = FastMCP("Calculator")

# DEFINE TOOLS

#addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print("CALLED: add(a: int, b: int) -> int:")
    return int(a + b)

@mcp.tool()
def add_list(l: list) -> int:
    """Add all numbers in a list"""
    print("CALLED: add(l: list) -> int:")
    return sum(l)

# subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print("CALLED: subtract(a: int, b: int) -> int:")
    return int(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print("CALLED: multiply(a: int, b: int) -> int:")
    return int(a * b)

#  division tool
@mcp.tool() 
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print("CALLED: divide(a: int, b: int) -> float:")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: int, b: int) -> int:
    """Power of two numbers"""
    print("CALLED: power(a: int, b: int) -> int:")
    return int(a ** b)

# square root tool
@mcp.tool()
def sqrt(a: int) -> float:
    """Square root of a number"""
    print("CALLED: sqrt(a: int) -> float:")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: int) -> float:
    """Cube root of a number"""
    print("CALLED: cbrt(a: int) -> float:")
    return float(a ** (1/3))

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    print("CALLED: factorial(a: int) -> int:")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: int) -> float:
    """log of a number"""
    print("CALLED: log(a: int) -> float:")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: int, b: int) -> int:
    """remainder of two numbers divison"""
    print("CALLED: remainder(a: int, b: int) -> int:")
    return int(a % b)

# sin tool
@mcp.tool()
def sin(a: int) -> float:
    """sin of a number"""
    print("CALLED: sin(a: int) -> float:")
    return float(math.sin(a))

# cos tool
@mcp.tool()
def cos(a: int) -> float:
    """cos of a number"""
    print("CALLED: cos(a: int) -> float:")
    return float(math.cos(a))

# tan tool
@mcp.tool()
def tan(a: int) -> float:
    """tan of a number"""
    print("CALLED: tan(a: int) -> float:")
    return float(math.tan(a))

# mine tool
@mcp.tool()
def mine(a: int, b: int) -> int:
    """special mining tool"""
    print("CALLED: mine(a: int, b: int) -> int:")
    return int(a - b - b)

@mcp.tool()
def create_thumbnail(image_path: str) -> Image:
    """Create a thumbnail from an image"""
    print("CALLED: create_thumbnail(image_path: str) -> Image:")
    img = PILImage.open(image_path)
    img.thumbnail((100, 100))
    return Image(data=img.tobytes(), format="png")

@mcp.tool()
def strings_to_chars_to_int(string: str) -> list[int]:
    """Return the ASCII values of the characters in a word"""
    print("CALLED: strings_to_chars_to_int(string: str) -> list[int]:")
    return [int(ord(char)) for char in string]

@mcp.tool()
def int_list_to_exponential_sum(int_list: list) -> float:
    """Return sum of exponentials of numbers in a list"""
    print("CALLED: int_list_to_exponential_sum(int_list: list) -> float:")
    return sum(math.exp(i) for i in int_list)

@mcp.tool()
def fibonacci_numbers(n: int) -> list:
    """Return the first n Fibonacci Numbers"""
    print("CALLED: fibonacci_numbers(n: int) -> list:")
    if n <= 0:
        return []
    fib_sequence = [0, 1]
    for _ in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence[:n]


@mcp.tool()
async def draw_rectangle(x1: int, y1: int, x2: int, y2: int) -> dict:
    """Draw a rectangle in Paint from (x1,y1) to (x2,y2)"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        print(f"Drawing rectangle from ({x1},{y1}) to ({x2},{y2})")
        
        # Get the Paint window and ensure it's active
        paint_window = paint_app.top_window()
        hwnd = paint_window.handle
        
        # Maximize and activate window
        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        time.sleep(1)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(1)
        
        # Get window dimensions
        window_rect = win32gui.GetWindowRect(hwnd)
        print(f"Window rect: {window_rect}")
        
        # Calculate canvas area (accounting for ribbon and borders)
        canvas_left = window_rect[0] + 10
        canvas_top = window_rect[1] + 160
        
        print(f"Canvas offset: left={canvas_left}, top={canvas_top}")
        
        # Calculate absolute coordinates
        abs_x1 = canvas_left + x1
        abs_y1 = canvas_top + y1
        abs_x2 = canvas_left + x2
        abs_y2 = canvas_top + y2
        
        print(f"Absolute coordinates: from ({abs_x1},{abs_y1}) to ({abs_x2},{abs_y2})")
        
        # Select rectangle tool using keyboard
        from pywinauto.keyboard import send_keys
        send_keys('^{TAB}')  # Ensure Home tab is active
        time.sleep(0.5)
        send_keys('{R}')     # Select rectangle tool
        time.sleep(1)
        
        # Use win32api for mouse control
        from win32api import SetCursorPos, mouse_event
        from win32con import MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP
        
        # Draw rectangle
        print("Starting rectangle drawing sequence")
        
        # Move to start position
        print(f"Moving to start position: ({abs_x1}, {abs_y1})")
        SetCursorPos((abs_x1, abs_y1))
        time.sleep(0.5)
        
        # Press left button
        print("Pressing left mouse button")
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Move to end position
        print(f"Moving to end position: ({abs_x2}, {abs_y2})")
        SetCursorPos((abs_x2, abs_y2))
        time.sleep(0.5)
        
        # Release left button
        print("Releasing left mouse button")
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        print("Rectangle drawing sequence completed")
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Rectangle drawn from ({x1},{y1}) to ({x2},{y2})"
                )
            ]
        }
    except Exception as e:
        print(f"Error in draw_rectangle: {str(e)}")
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error drawing rectangle: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def add_text_in_paint(text: str) -> dict:
    """Add text in Paint"""
    global paint_app
    try:
        if not paint_app:
            return {
                "content": [
                    TextContent(
                        type="text",
                        text="Paint is not open. Please call open_paint first."
                    )
                ]
            }
        
        # Get the Paint window
        paint_window = paint_app.top_window()
        time.sleep(0.5)  # Wait for window to be ready
        
        # Get window handle
        hwnd = paint_window.handle
        
        # Ensure Paint window is active
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.5)
        
        # Get window coordinates for text placement (center of the rectangle)
        rect = win32gui.GetWindowRect(hwnd)
        text_x = rect[0] + 250 + 10  # Center horizontally (with window offset)
        text_y = rect[1] + 250 + 160  # Center vertically (with window offset)
        
        # Select text tool using keyboard shortcut
        from pywinauto.keyboard import send_keys
        send_keys('{T}')  # 'T' is the shortcut for text tool
        time.sleep(0.5)
        
        # Click where to add text
        from win32api import SetCursorPos, mouse_event
        from win32con import MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP
        
        SetCursorPos((text_x, text_y))
        time.sleep(0.3)
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.2)
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        time.sleep(0.5)
        
        # Type the text
        send_keys(text, with_spaces=True)
        time.sleep(0.3)
        
        # Click outside to finish text editing
        SetCursorPos((text_x + 100, text_y + 100))
        time.sleep(0.3)
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(0.2)
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Text:'{text}' added successfully"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        }

@mcp.tool()
async def open_paint() -> dict:
    """Open Microsoft Paint"""
    global paint_app
    try:
        # Start Paint
        paint_app = Application(backend='uia').start('mspaint.exe')
        time.sleep(1)  # Wait for Paint to open
        
        # Get the Paint window
        paint_window = paint_app.window(class_name='MSPaintApp')
        
        # Maximize the window
        paint_window.maximize()
        time.sleep(0.5)
        
        return {
            "content": [
                TextContent(
                    type="text",
                    text="Paint opened successfully and maximized"
                )
            ]
        }
    except Exception as e:
        return {
            "content": [
                TextContent(
                    type="text",
                    text=f"Error opening Paint: {str(e)}"
                )
            ]
        }

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    print("CALLED: get_greeting(name: str) -> str:")
    return f"Hello, {name}!"


# DEFINE AVAILABLE PROMPTS
@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"
    print("CALLED: review_code(code: str) -> str:")


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    # Check if running with mcp dev command
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution
