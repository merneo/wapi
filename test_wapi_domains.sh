#!/usr/bin/env expect
set timeout 60

set ssh_host "37.205.13.204"
set ssh_port "1991"
set ssh_user "torwn"
set ssh_pass "Adam.H0ps"
set wapi_login "adam.chmelicku@gmail.com"

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
    timeout {
        puts "Connection timeout"
        exit 1
    }
}

puts "\n=== Checking wapi installation ==="
send "which wapi && wapi --help 2>&1 | head -3\r"
expect "$ "

puts "\n=== Checking configuration ==="
send "ls -la ~/.config/wapi/ 2>&1 || echo 'Config dir not found'\r"
expect "$ "

send "cat ~/.config/wapi/config.env 2>&1 | head -5 || echo 'Config file not found'\r"
expect "$ "

puts "\n=== Testing domain list (should show error if not configured) ==="
send "wapi domain list 2>&1\r"
expect "$ "

puts "\n=== Testing domain info with a test domain ==="
send "wapi domain info example.com 2>&1 | head -10\r"
expect "$ "

puts "\n=== Testing search command (doesn't need auth) ==="
send "wapi search example.com 2>&1 | head -15\r"
expect "$ "

puts "\n=== Testing auth status ==="
send "wapi auth status 2>&1\r"
expect "$ "

puts "\n=== Checking if we can get domain list with proper config ==="
send "wapi config show 2>&1\r"
expect "$ "

puts "\n=== Testing DNS commands ==="
send "wapi dns records example.com 2>&1 | head -10\r"
expect "$ "

puts "\n=== Summary ==="
send "echo 'wapi installation check complete'\r"
expect "$ "

send "exit\r"
expect eof

puts "\n=== Remote Test Complete ==="
