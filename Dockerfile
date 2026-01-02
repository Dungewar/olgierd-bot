# Use a lightweight version of Python
# (Ensure this matches the version you use, e.g., 3.11, 3.12)
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy just the requirements first (this helps speed up re-builds)
COPY requirements.txt .

# Install dependencies
# --no-cache-dir keeps the image small
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of your code
COPY . .

# The command to start your bot
# Change 'main.py' to whatever your bot's entry file is!
CMD ["python", "main.py"]