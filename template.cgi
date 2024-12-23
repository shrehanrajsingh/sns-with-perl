#!/usr/bin/perl

package Template;

require './utils.cgi';
require './conn.cgi';

# parse (cont, params, lexicals)
sub parse {
    my $cont = shift;
    my %params = %{shift @_};
    my %lexicals = %{shift @_};

    for my $key (keys %params) {
        # print "[$key]\t";
        # print scalar $params{$key};
    }
    # print "----\n";

    my $res = "";
    my @cont_split = split /\n/, $cont;
    my $clim = scalar(@cont_split) - 1;
    my $i = 0;

    while ($i <= $clim) {
        my $line = $cont_split[$i];
        # if ( $line =~ m/\=\{\$([a-zA-Z0-9]+)\}/ ) {
        #     print "$params{$1}\n";
        # }

        # for my $k (keys %lexicals) {
        #     print "$k  ";
        # }
        # print "<br>";

        my $pres_line = $line;

        $line =~ s/\=\{\s*\$([a-zA-Z0-9_]+)\s*\}/"$params{$1}"/eg;
        $line =~ s/\=\{\s*\$([a-zA-Z0-9_]+)\[[(\'\")]([a-zA-Z0-9_]+)[\'\"]\]\s*\}/%{$params{$1}}{$2}/eg;
        $line =~ s/\=\{\s*\%([a-zA-Z0-9_]+)\s*\}/"$lexicals{$1}"/eg;
        $line =~ s/\=\{\s*\%([a-zA-Z0-9_]+)\[[(\'\")]([a-zA-Z0-9_]+)[\'\"]\]\s*\}/%{$lexicals{$1}}{$2}/eg;
        $line =~ s/\=\{\s*const\s*\"(.*)\"\}/"$1"/eg;
        $line =~ s/\\\=\{/\=\{/;

        if ( $line =~ m/[^\\]\=\{\s*\bfor\b\s*\%([a-zA-Z0-9_]+)\:\s*\$([a-zA-Z0-9_]+)\s*\}/ ) {
            my $vr = $1;
            my $it = $2;

            # Find <end>
            my $ec = 0;
            my $j = $i + 1;
            my $p = "";

            while ($j <= $clim) {
                my $jv = $cont_split[$j];

                if ( $jv =~ m/\=\{\s*for/ or
                    $jv =~ m/\=\{\s*if/ ) {
                    $ec++;
                }

                if ( $jv =~ m/\=\{\s*end\s*\}/ ) {
                    if ( $ec ) {
                        $ec--;
                    } else {
                        last;
                    }
                }

                $j++;
                $p = $p . "$jv\n";
            }

            my @arr = @{$params{$it}};
            my $fp = "";
            
            for my $akey (@arr) {
                my $cur = Template::parse($p, (
                    {%params}, {
                        %lexicals,
                        $vr => $akey
                    }
                ));

                $fp = $fp . "$cur\n";
            }

            $line = $fp;
            $i = $j;
        }

        if ( $line =~ m/\=\{\s*var\s*([a-zA-Z0-9_]+)\s*:\s*([a-zA-Z0-9_]+)\s*([^}]+)\s*\}/ ) {
            my $vname = $1;
            my $call = $2;
            my $arg = $3; # take only 1 argument
            # print "($vname) ($call) ($arg)\n";

            $arg = "={$arg}";
            $arg = Template::parse($arg, {%params}, {
                %lexicals,
            });

            $arg = util::trim($arg);
            
            if ( $call eq "getuser" ) {
                my @data = conn::get_data($conn::DB_NAME{user}, "users", (
                    ID => $arg
                ));

                $lexicals{$vname} = $data[0];

                # for my $k (keys %lexicals) {
                #     print "$k ($lexicals{$k})<br>";
                # }
                $i++;
                next;
            }
        }

        if ( $line =~ m/\=\{\s*time\s*([^}]+)\s*\}/ ) {
            my $arg = $1;
            $arg = "={$arg}";
            $arg = Template::parse($arg, {%params}, {
                %lexicals,
            });

            $arg = util::trim($arg);

            $line = "" . localtime($arg);
        }

        if ( $line =~ m/\=\{\s*if\s*\((.*)\)\s*(eq|neq)\s*\((.*)\)\s*\}/ ) {
            my $arg1 = $1;
            my $call = $2;
            my $arg2 = $3;

            # print "($arg1) ($call) ($arg2) <br>";

            $arg1 = "={$arg1}";
            $arg2 = "={$arg2}";

            $arg1 = Template::parse($arg1, {%params}, {
                %lexicals
            });

            $arg2 = Template::parse($arg2, {%params}, {
                %lexicals
            });

            $arg1 = util::trim($arg1);
            $arg2 = util::trim($arg2);

            # print "($arg1) ($call) ($arg2) <br>";

            my $ec = 0;
            my $j = $i + 1;
            my $p = "";
            my $else_idx = 0;

            while ($j <= $clim) {
                my $jv = $cont_split[$j];

                if ( $jv =~ m/\=\{\s*for/ or
                    $jv =~ m/\=\{\s*if/ ) {
                    $ec++;
                }

                if ( $jv =~ m/\=\{\s*else\s*\}/ ) {
                    $else_idx = $j;
                }

                if ( $jv =~ m/\=\{\s*end\s*\}/ ) {
                    if ( $ec ) {
                        $ec--;
                    } else {
                        last;
                    }
                }

                $j++;
            }

            # print "($arg1) ($arg2)\n";

            if ( ($call eq 'eq' and $arg1 eq $arg2) or
                ($call eq 'neq' and !($arg1 eq $arg2)) ) {
                    $cont_split[$j] = "";

                    if ( $else_idx ) {
                        while ( $else_idx < $j ) {
                            $cont_split[$else_idx] = "";
                            $else_idx++;
                        }
                    }
            } else {
                if ( $else_idx ) {
                    $cont_split[$j] = "";
                    $i = $else_idx;
                } else {
                    $i = $j;
                }
            }
            
            $i++;
            next;
        }

        $res = $res . "$line\n";

        $i++;
    }

    return $res;
};

sub readfile {
    my $fname = shift;
    my $res = "";

    open(FILE_H, '<', $fname);

    while (my $line = <FILE_H>) {
        $res = $res . $line;
    }

    close(FILE_H);
    return $res;
};

# print parse(Template::readfile('home.html'), {
#     allstatus => [{
#         ID => '1'
# }]
# }, {});

1;