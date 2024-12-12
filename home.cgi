#!/usr/bin/perl

use CGI;

require './conn.cgi';
require './utils.cgi';
require './template.cgi';

my $q = CGI->new;
my $ck = $q->cookie('UU') || undef;

unless ( $ck ) {
    print $q->redirect('./index.cgi');
    exit (0);
}
my %det = conn::get_user_from_uuid($ck);

unless ( scalar keys %det ) {
    print $q->header( 
        -type => 'text/html', 
        -cookie => $q->cookie( 
            -name => 'UU', 
            -value => '()', 
            -expires => '-1d' 
        ),
        -status => '500 Internal Server Error');
    
    print <<EOM;
<h1>Invalid auth token.</h1>
<p>Kindly relogin again</p>
<a href='./index.cgi'>Home</a>
EOM
    
    exit(0);
}

print $q->header("text/html");

# username email passwd ID
# for my $k (keys %det) {
#     print "($k)\n";
# }

my @allstatus = conn::get_data($conn::DB_NAME{status}, "status", (
    UID => $det{ID}
));

@allstatus = sort { $b->{ultime} <=> $a->{ultime} } @allstatus;

# for my $key (@allstatus) {
#     my %k = %{$key};
#     print "$k{content}\n";
# }

print Template::parse(Template::readfile('home.html'), {
    uname => $det{username},
    email => $det{email},
    id => $det{ID},
    allstatus => [@allstatus],
    _time => scalar(localtime()),
}, {});