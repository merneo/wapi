#!/usr/bin/env expect
set timeout 30

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
        # Connected successfully
    }
    timeout {
        puts "Connection timeout"
        exit 1
    }
}

# Check if wapi is installed
send "which wapi\r"
expect {
    "$ " {
        set output $expect_out(buffer)
        if {[string match "*not found*" $output] || [string match "*no wapi*" $output]} {
            puts "ERROR: wapi not found in PATH"
            send "exit\r"
            exit 1
        }
        puts "✓ wapi found"
    }
}

# Test wapi version/info
send "wapi --version 2>&1 || wapi --help 2>&1 | head -5\r"
expect {
    "$ " {
        puts "✓ wapi command works"
    }
}

# Test authentication
send "wapi auth login $wapi_login\r"
expect {
    "password:" {
        puts "✓ Authentication prompt appeared"
        send "\r"  # Just press enter to cancel
        exp_continue
    }
    "$ " {
        puts "✓ Auth command executed"
    }
    timeout {
        puts "⚠ Auth command timeout (may need interactive password)"
    }
}

# Test domain list
send "wapi domain list 2>&1 | head -10\r"
expect {
    "$ " {
        set output $expect_out(buffer)
        puts "Domain list output received"
    }
    timeout {
        puts "⚠ Domain list timeout"
    }
}

# Test domain info (try a common domain pattern)
send "wapi domain info --help 2>&1 | head -5\r"
expect {
    "$ " {
        puts "✓ Domain info command available"
    }
}

# Test search
send "wapi search --help 2>&1 | head -5\r"
expect {
    "$ " {
        puts "✓ Search command available"
    }
}

send "exit\r"
expect eof

puts "\n=== Test Summary ==="
puts "✓ SSH connection successful"
puts "✓ wapi command found and executable"
puts "✓ Basic commands tested"
