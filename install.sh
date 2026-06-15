#!/bin/bash
# Load Balancer Analyzer - Complete Linux Installation Script
# Save as: install.sh
# Run: chmod +x install.sh && ./install.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Load Balancer Analyzer - Installation${NC}"
echo -e "${BLUE}========================================${NC}"

# Check Python
echo -e "\n${YELLOW}[1/4] Checking Python...${NC}"
if command -v python3 &>/dev/null; then
    echo -e "${GREEN}✓${NC} Python3: $(python3 --version)"
else
    echo -e "${RED}✗ Python3 not found. Installing...${NC}"
    sudo apt update && sudo apt install -y python3 python3-pip
fi

# Check/Install pip
echo -e "\n${YELLOW}[2/4] Checking pip...${NC}"
if command -v pip3 &>/dev/null; then
    echo -e "${GREEN}✓${NC} pip3 found"
else
    echo -e "${RED}✗ pip3 not found. Installing...${NC}"
    sudo apt install -y python3-pip
fi

# Upgrade pip
echo -e "\n${YELLOW}[3/4] Upgrading pip...${NC}"
pip3 install --upgrade pip --quiet

# Install dependencies
echo -e "\n${YELLOW}[4/4] Installing Python packages...${NC}"

# Install all required packages
pip3 install requests>=2.25.0 --quiet
pip3 install fake-useragent>=1.1.1 --quiet
pip3 install colorama>=0.4.4 --quiet
pip3 install urllib3>=1.26.0 --quiet
pip3 install certifi>=2020.12.0 --quiet

# Create requirements.txt
cat > requirements.txt << 'EOF'
requests>=2.25.0
fake-useragent>=1.1.1
colorama>=0.4.4
urllib3>=1.26.0
certifi>=2020.12.0
EOF

# Verify installation
echo -e "\n${YELLOW}Verifying installation...${NC}"
python3 -c "import requests; print(f'${GREEN}✓${NC} requests: ' + requests.__version__)" 2>/dev/null || echo -e "${RED}✗ requests failed${NC}"
python3 -c "from fake_useragent import UserAgent; print(f'${GREEN}✓${NC} fake-useragent installed')" 2>/dev/null || echo -e "${RED}✗ fake-useragent failed${NC}"
python3 -c "from colorama import init; print(f'${GREEN}✓${NC} colorama installed')" 2>/dev/null || echo -e "${RED}✗ colorama failed${NC}"

# Make main script executable if exists
if [ -f "lb_analyzer.py" ]; then
    chmod +x lb_analyzer.py
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${BLUE}To run the tool:${NC}"
echo -e "  python3 lb_analyzer.py -u http://target.com"
echo -e "\n${BLUE}Or download the main script:${NC}"
echo -e "  curl -O https://raw.githubusercontent.com/YOURUSERNAME/load-balancer-analyzer/main/lb_analyzer.py"
echo -e "  python3 lb_analyzer.py -u http://balancer.hackycorp.com"
