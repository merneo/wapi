#!/usr/bin/env expect
set timeout 120

set ssh_host "37.205.13.204"
set ssh_port "1991"
set ssh_user "torwn"
set ssh_pass "Adam.H0ps"
set wapi_login "adam.chmelicku@gmail.com"
set wapi_pass "Adam.H0ps"

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

puts "\n=== Step 1: Updating wapi to latest version ==="
send "cd ~/.local/wapi && source venv/bin/activate && pip install --upgrade --force-reinstall \"wapi-cli @ https://github.com/merneo/wapi/archive/refs/heads/master.zip#egg=wapi-cli\" 2>&1 | tail -5\r"
expect "$ "

puts "\n=== Step 2: Setting WAPI_FORCE_IPV4=true ==="
send "wapi config set WAPI_FORCE_IPV4 true 2>&1\r"
expect "$ "

puts "\n=== Step 3: Testing auth login with IPv4-only mode ==="
send "wapi auth login --username $wapi_login --password $wapi_pass 2>&1\r"
expect {
    "$ " {
        puts "✓ Command completed"
    }
    timeout {
        puts "⚠ Timeout"
    }
}

puts "\n=== Step 4: Checking config ==="
send "wapi config show 2>&1\r"
expect "$ "

puts "\n=== Step 5: Testing auth status ==="
send "wapi auth status 2>&1\r"
expect "$ "

send "exit\r"
expect eof

puts "\n=== Test Complete ==="
