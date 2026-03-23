# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import uvicorn


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
    )

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
