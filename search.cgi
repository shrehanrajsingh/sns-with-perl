#!/usr/bin/perl

use CGI;

require './conn.cgi';
require './utils.cgi';
require './template.cgi';

my $q = CGI->new;
my $ck = $q->cookie('UU');

unless ( $ck ) {
    print $q->redirect('./index.cgi');
    exit (0);
}

print $q->header('text/html');

my $phrase = $q->param('phrase');
my @gd = conn::get_data_like($conn::DB_NAME{user}, "users", (
    username => $phrase,
));

# for my $val (@gd) {
#     my %hs = %{$val};

#     for my $key (keys %hs) {
#         print "$key: $hs{$key}\t";
#     }
#     print "\n";
# }

print Template::parse(Template::readfile('search.html'), {
    phrase => util::trim( $phrase ),
    usermatch => [@gd]
}, {});