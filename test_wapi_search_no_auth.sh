#!/usr/bin/env expect
set timeout 60

set ssh_host "37.205.13.204"
set ssh_port "1991"
set ssh_user "torwn"
set ssh_pass "Adam.H0ps"

spawn ssh -p $ssh_port $ssh_user@$ssh_host

expect {
    "password:" {
        send "$ssh_pass\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    "$ " {
        # Connected
    }
}

puts "\n=== Testing search without full config (should use WHOIS) ==="
# Temporarily remove password from config to test WHOIS-only mode
send "mv ~/.config/wapi/config.env ~/.config/wapi/config.env.backup 2>/dev/null || true\r"
expect "$ "

send "echo 'WAPI_USERNAME=test@example.com' > ~/.config/wapi/config.env\r"
expect "$ "

puts "\n=== Testing search with example.com (should use WHOIS) ==="
send "wapi search example.com 2>&1 | head -25\r"
expect "$ "

puts "\n=== Testing search with google.com (should show registered) ==="
send "wapi search google.com 2>&1 | head -25\r"
expect "$ "

puts "\n=== Restoring config ==="
send "mv ~/.config/wapi/config.env.backup ~/.config/wapi/config.env 2>/dev/null || true\r"
expect "$ "

send "exit\r"
expect eof

puts "\n=== Search Test Complete ==="
