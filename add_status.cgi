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
    print $q->redirect('./index.cgi');
    exit(0);
}

if ( $ENV{REQUEST_METHOD} eq 'POST' ) {
    my %form_data = $q->Vars;
    my $cont = $form_data{status};

    if ( conn::add_data($conn::DB_NAME{status}, "status", (
        ID => conn::primkey($conn::DB_NAME{status}, "status"),
        UID => $det{ID},
        ultime => "" . time,
        content => $cont
    )) ) {
    print $q->header( -type => 'text/html', -status => '500 Internal Server Error' );
    print <<EOM;
<h1>500 Internal Server Error</h1>
<p>Error message: $conn::LAST_ERROR</p>
<a href='./index.cgi'>Home</a>
EOM
        exit(0);
    }
}

print $q->redirect('./home.cgi');