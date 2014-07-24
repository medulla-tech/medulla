#!/bin/sh

# This script generates 
echo $(dirname $0)
cd $(dirname $0)

# Generate deb agents
linux/deb/generate.sh

# Generate win32 agents
win32/generate-agent-pack.sh

# Generate mac agents
./generate-agents
