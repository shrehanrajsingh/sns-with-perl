#!/usr/bin/perl

use CGI;

require './conn.cgi';

my $q = CGI->new;

unless ( $ENV{ REQUEST_METHOD } eq 'POST' ) {
    print $q->redirect('./index.cgi');
    exit(0);
}

unless ( exists $ENV{ HTTP_REFERER } ) {
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

my @dcheck = conn::get_data($conn::DB_NAME{user}, "users", 
    username => $form_data{suname},
    email => $form_data{suemail}
);

if ( scalar(@dcheck) > 0) {
    print $q->header(-type => 'text/html', -status => '400 Bad Request');
    print "<h1>400 Bad Request</h1><p>User already exists, consider logging in</p>";
    print "<a href='./index.cgi'>Home</a>";
    exit(0);
}

if ( conn::add_data($conn::DB_NAME{user}, "users", (
    ID => conn::primkey($conn::DB_NAME{user}, "users"),
    username => $form_data{suname},
    email => $form_data{suemail},
    passwd => conn::encrypt_btwp($form_data{supwd})
)) ) {
    print $q->header(-type => 'text/html', -status => '400 Bad Request');
    print "<h1>($conn::LAST_ERROR)</h1>";
    exit (0);
}

print $q->header(-type => 'text/html', -status => '200 OK');
print $q->h1("Signup Successful!"),
        "<a href='./index.cgi'>Home</a>";