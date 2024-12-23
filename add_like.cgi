#!/usr/bin/perl

require './conn.cgi';
require './utils.cgi';

use CGI;

my $q = CGI->new;
my $ck = $q->cookie('UU');

unless ( $q->request_method eq 'POST' ) {
    print $q->redirect('./index.cgi');
}

unless ( $ck ) {
    print $q->redirect('./index.cgi');
}

my %det = conn::get_user_from_uuid($ck);

my $vars = $q->param('POSTDATA');

my @sp = split /&/, $vars;
my %vhash;

for (@sp) {
    my @s = split /=/, $_;
    $vhash{$s[0]} = $s[1];
}

if ( $vhash{type} eq 'like' ) {
    $vhash{type} = 'L';

} elsif ( $vhash{type} eq 'dislike' ) {
    $vhash{type} = 'D';
}

if ( $vhash{type} eq 'L' or $vhash{type} eq 'D' ) {
    if ( conn::add_data($conn::DB_NAME{likes}, "likes", (
        ID => conn::primkey($conn::DB_NAME{likes}, "likes"),
        Status_ID => $vhash{sid},
        Like_Type => $vhash{type},
        ltime => "" . time,
        Liker_ID => $det{ID}
    ))) {
            print $q->header( -type => "application/json", -status => "500 Internal Server Error" );
            print <<EOM;
        {
            "error": "$conn::LAST_ERROR"
        }
EOM
    }
}

if ( $vhash{type} eq 'unlike' ) {
    if ( conn::remove_data($conn::DB_NAME{likes}, "likes", (
        Status_ID => $vhash{sid},
        Like_Type => $vhash{type},
        Liker_ID => $det{ID}
    ))) {
            print $q->header( -type => "application/json", -status => "500 Internal Server Error" );
            print <<EOM;
        {
            "error": "$conn::LAST_ERROR"
        }
EOM
    }
}

print $q->header('application/json');