#!/usr/bin/env bash

# Global config
sudo mkdir -p /etc/profile.d
sudo starship preset nerd-font-symbols -o /etc/starship.toml
echo 'export STARSHIP_CONFIG=/etc/starship.toml' | sudo tee /etc/profile.d/starship.sh >/dev/null

# Enable for all bash users (Debian/Ubuntu). Fall back for Alpine.
if [ -f /etc/bash.bashrc ]; then
  if ! grep -q 'starship init bash' /etc/bash.bashrc; then
    echo 'eval "$(starship init bash)"' | sudo tee -a /etc/bash.bashrc >/dev/null
  fi
else
  if ! grep -q 'starship init bash' /etc/profile; then
    echo 'eval "$(starship init bash)"' | sudo tee -a /etc/profile >/dev/null
  fi
fi