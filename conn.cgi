#!/usr/bin/perl

package conn;

use CGI;
use MIME::Base64;

our $LAST_ERROR = "";
our $E_SALT = '/A'; # combination of any two letters from ('.', '/', 0..9, 'A'..'Z', 'a'..'z')
my $q = new CGI;

our $DB_DIR = `pwd`;
chop($DB_DIR);
$DB_DIR = $DB_DIR . "/database";

our %DB_NAME = (
    user => "$DB_DIR/users.db",
    status => "$DB_DIR/status.db",
    user_uid => "./user_uid",
);

sub check_dbs {
    for my $key (keys %DB_NAME) {
        my $fname = $DB_NAME{$key};

        unless ( -e -w $fname ) {
            open (TMP_FH, ">", $fname);
            close (TMP_FH);

            open (TMP_FH_CONF, ">", "$fname.conf");

            print TMP_FH_CONF <<CONF_CONTENT;
Begin Headers
    Delimeter=,
End Headers

CONF_CONTENT

            close (TMP_FH_CONF);
        }
    }
};

# table_exists (db_name, table_name);
sub table_exists {
    my ($db_name, $table_name) = @_;

    open (DB_F, "<", "$db_name.conf");

    my $last_line;
    my $t_e = 0;

    while (my $line = <DB_F>) {
        $line =~ s/^\s+//;
        $line =~ s/\s+$//;

        if ( $line eq "Name=$table_name"
             and $last_line eq 'Begin Table') {
                $t_e = 1;
                last;
             }

        $last_line = $line;
    }

    close (DB_F);
    return $t_e;
};

# column_exists (db_name, table_name, column_name);
sub column_exists {
    my ($db_name, $table_name, $column_name) = @_;

    open (DB_F, "<", "$db_name.conf");
    my $curr_table = "";
    my $saw_clm = 0;

    INW0: while (my $line = <DB_F>) {
        next INW0 if $line eq "\n";

        $line =~ s/^\s+//;
        $line =~ s/\s+$//;

        if ( $line eq 'Begin Table' ) {
            while (my $nl = <DB_F>) {
                unless ( $nl =~ m/\s*\bName=/ ) {
                    next;
                }

                $curr_table = $1 if $nl =~ m/\s*\bName=(\w+)/;
                last;
            }

            next;
        }

        if ( $line eq 'Begin Column'
             and $curr_table eq $table_name ) {
                my $cln = "";

            INW1: while (my $ln = <DB_F>) {

                if ( $ln =~ m/\s*\bName=/ ) {
                    $cln = $1 if $ln =~ m/\s*\bName=(\w+)/;
                    last INW1;
                }
            }

            if ( $cln and $cln eq $column_name ) {
                $saw_clm = 1;
                last;
            }
        }

        if ( $line eq 'End Table' 
             and $curr_table eq $table_name) {

                $saw_clm = 0;
                last;
             }

        
    }

    close (DB_F);
    return $saw_clm;
}

# create_table (db_name, table_name, column_type)
# column_type is a hash with names as name of column and 
# value can only be "Int" or "String";

sub create_table {
    my $db_name = shift;
    my $table_name = shift;
    my %column_hash = @_;

    if ( table_exists($db_name, $table_name) ) {
        $conn::LAST_ERROR = "table_already_exists";
        return 1;
    }

    open (CONF_HANDLER, ">>", "$db_name.conf") or die "Cannot open file $db_name.conf";
    print CONF_HANDLER <<TABLE_DATA;

Begin Table
    Name=$table_name

TABLE_DATA

    foreach my $name (keys %column_hash) {
        print CONF_HANDLER <<COLUMN_DATA;
    Begin Column
        Name=$name
        Type=$column_hash{$name}
    End Column

COLUMN_DATA
    }

    print CONF_HANDLER "End Table\n";
    close (CONF_HANDLER);

    return 0;
};

# add_data (db_name, table_name, data)
sub add_data {
    my $db_name = shift;
    my $table_name = shift;
    my %data = @_;

    unless ( -e -w $db_name ) {
        $LAST_ERROR = "db_does_not_exist";
        return 1;
    }

    unless ( table_exists($db_name, $table_name) ) {
        $LAST_ERROR = "table_does_not_exist";
        return 1;
    }

    open (DB_F, ">>", $db_name);
    print DB_F "%=\ntable $table_name\n";

    for my $name (keys %data) {
        my $cd = encrypt_bt($data{$name});
        print DB_F "$name $cd\n";
    }

    print DB_F "=%\n";
    close (DB_F);
    return 0;
};

# get_data (db_name, table_name, data)
sub get_data {
    my $db_name = shift;
    my $table_name = shift;
    my %data = @_;
    my %dc; # current data chit
    my @res;

    unless ( -e $db_name ) {
        $LAST_ERROR = "db_does_not_exist";
        return @res;
    }

    unless ( table_exists($db_name, $table_name) ) {
        $LAST_ERROR = "table_does_not_exist";
        return @res;
    }

    open (DB_F, "<", $db_name);

    while (my $line = <DB_F>) {
        if ( $line eq "%=\n" ) {
            my $nl = <DB_F>;

            unless ( $nl eq "table $table_name\n" ) {
                while (!($nl eq "=%\n")) {
                    $nl = <DB_F>;
                }

                next;
            }

            $nl = <DB_F>;
            LINEIT: while (!($nl eq "=%\n")) {
                my @spl = split(" ", $nl, 2);
                chomp($spl[1]);
                $dc{$spl[0]} = $spl[1];
                # print "$spl[0]: $dc{$spl[0]}\n";
                $nl = <DB_F>;
            }

            my $diff = 0;
            for my $name (keys %data) {
                unless ( exists $dc{$name} 
                     and $data{$name} eq decrypt_bt($dc{$name}) ) {
                        $diff = 1;
                        last;
                }
            }

            if ( !$diff ) {

                for my $i (keys %dc) {
                    $dc{$i} = decrypt_bt($dc{$i});
                    # print "$dc{$i}\n";
                }
                # print "<br>";
                my %r;

                for my $k (keys %dc) {
                    $r{$k} = $dc{$k};
                }

                push(@res, \%r);
            }
        }
    }

    close (DB_F);
    return @res;
};

# primkey (db_name, table_name)
# Returns the primary key for the data which will be added next.
# Returns the number of "data chits" currently in database (1 indexed)
# If there are 4 data chits, primkey returns 4
# as the next primary key for data chit (0 indexed) will be 4
sub primkey {
    my ($db_name, $table_name) = @_;

    unless ( -e -r $db_name ) {
        $LAST_ERROR = "db_does_not_exist";
        return 1;
    }

    unless ( table_exists($db_name, $table_name) ) {
        $LAST_ERROR = "table_does_not_exist";
        return 1;
    }

    open (DB_F, "<", $db_name);
    my $ct = 0;

    while (my $line = <DB_F>) {

        if ( $line eq "%=\n" ) {
            my $nl = <DB_F>;

            if ( $nl eq "table $table_name\n" ) {
                $ct++;
            }

            while (!($nl eq "=%\n")) {
                $nl = <DB_F>;
            }
        }
    }

    close (DB_F);
    return $ct;
};

# encrypt_bt (data)
# Use for everything other than passwords
sub encrypt_bt {
    my $data = shift;

    # Rotate 13
    $data =~ tr /[a-m][A-M][n-z][N-Z]/[n-z][N-Z][a-m][A-M]/;
    # Swap case
    $data =~ tr /[a-z][A-Z]/[A-Z][a-z]/;
    # Change numbers
    $data =~ tr/[0123456789]/[0987654321]/;
    # Perl encryption
    # $data = crypt $data, join "", $E_SALT;

    return $data;
};

# encrypt_btwp (data)
# Uses perl's crypt routine
# Cannot be decrypted
# Use for passwords
sub encrypt_btwp {
    my $data = shift;

    $data = conn::encrypt_bt($data);
    # Perl encryption
    $data = crypt $data, join "", $E_SALT;
    # Remove salt
    substr($data, 2);

    return $data;
};

# decrypt_bt (data)
sub decrypt_bt {
    my $data = shift;

    $data =~ tr/[0987654321]/[0123456789]/;
    $data =~ tr /[A-Z][a-z]/[a-z][A-Z]/;
    $data =~ tr /[n-z][N-Z][a-m][A-M]/[a-m][A-M][n-z][N-Z]/;

    return $data;
};

# get_user_from_uuid(UU)
sub get_user_from_uuid {
    my $UU = shift;
    my $key = undef;
    my $sawkey = 0;

    open(HANDLE, '<', $DB_NAME{user_uid});

    while (my $line = <HANDLE>) {
        my @sp = split / /, $line, 2;

        if ( util::trim($sp[1]) eq $UU ) {
            $key = $sp[0];
            $sawkey = 1;
            last;
        }
    }

    unless ( $sawkey ) {
        return ();
    }

    close(HANDLE);
    my @r = conn::get_data($DB_NAME{user}, "users", (
        ID => "$key"
    ));

    return %{$r[0]};
}

# get_data_like (db_name, table_name, like_dict)
sub get_data_like {
    my $db_name = shift;
    my $table_name = shift;
    my %like_d = @_;
    my @res;

    open(DB_F, '<', $db_name);

    while (my $line = <DB_F>) {

        if ( $line eq "%=\n" ) {
            my $nl = <DB_F>;

            if ( $nl eq "table $table_name\n" ) {
                my %dc;
                
                while (!($nl eq "=%\n")) {

                    my @sp = split / /, $nl, 2;
                    $dc{$sp[0]} = conn::decrypt_bt(util::trim($sp[1]));
                    $nl = <DB_F>;
                }

                for my $key (keys %like_d) {
                    if ( $dc{$key} =~ m/\Q$like_d{$key}\E/ ) {
                        my %r;

                        for my $key (keys %dc) {
                            $r{$key} = $dc{$key};
                        }

                        push(@res, \%r);
                    }
                }
            } else {
                while (!($line eq "=%\n")) {

                    $line = <DB_F>;
                    next;
                }
            }
        }
    }

    close(DB_F);
    return @res;
}

check_dbs();

# No GET requests allowed
if ( $q->request_method eq 'GET'
     and $q->self_url =~ /\bconn.cgi\b/ ) {

    print $q->header ( -type => "text/html", -status => "405 Not Allowed" );
}

1;