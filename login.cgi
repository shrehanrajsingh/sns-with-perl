#!/usr/bin/perl

use CGI;
use MIME::Base64;

require './conn.cgi';
require './utils.cgi';

my $q = CGI->new;

unless ( $ENV{REQUEST_METHOD} eq 'POST' ) {
    print $q->redirect('./index.cgi');
    exit(0);
}

unless ( exists $ENV{HTTP_REFERER} ) {
    print $q->header(-type => 'text/html', -status => '400 Bad Request');
    print "<h1>400 Bad Request</h1><p>Missing HTTP_REFERER</p>";
    exit(0);
}

my $expected_referer = "$ENV{HTTP_ORIGIN}$ENV{CONTEXT_PREFIX}myforum/index.cgi";
unless ( $ENV{ HTTP_REFERER } eq $expected_referer ) {
    print $q->header(-type => 'text/html', -status => '400 Bad Request');
    print "<h1>400 Bad Request</h1><p>Invalid HTTP_REFERER</p>";
    exit(0);
}

my %form_data = $q->Vars;
my $uname = $form_data{uname};
my $upwd = $form_data{upwd};

my @dcheck = conn::get_data($conn::DB_NAME{user}, "users", (
    username => $uname,
    passwd => conn::encrypt_btwp($upwd)
));

unless ( scalar(@dcheck) ) {
    print $q->header (-type => 'text/html', -status => '200 OK');
    print "<h1>Account does not exist, please create one.</h1><br>";
    print "<a href='./index.cgi'>Home</a><br>";
    print "$conn::LAST_ERROR<br>";
    exit(0);
}

unless ( scalar(@dcheck) == 1 ) {
    print $q->header (-type => 'text/html', -status => '500 Internal Server Error');
    print "<h1>Internal Server Error</h1>";
    exit(0);
}

my %dc = %{ @dcheck[0] };

# Create secure token (a unique identifier)
my $tok = "$uname;$upwd" . time;
$tok = encode_base64($tok);
chomp($tok);

# Add to uid file
# print $q->header (-type => 'text/plain');
util::append_to_file($conn::DB_NAME{user_uid}, "$dc{ID} $tok");

# Send the unique id as a cookie
$ck = $q->cookie( -name => "UU", -value => "$tok", -path => "/", -expires => "+1M");
print $q->header( -type => 'text/html', -cookie => $ck, -location => './home.cgi' );