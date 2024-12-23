#!/usr/bin/perl

require './utils.cgi';
require './conn.cgi';
require './template.cgi';

use CGI;

my $q = CGI->new;
my $ck = $q->cookie('UU');
my %det = conn::get_user_from_uuid($ck);

unless ( $ck ) {
    redirect('./index.cgi');
}

unless ( $q->param( 'name' ) ) {
    print $q->redirect( './index.cgi' );
    exit (1);
}

my $name = $q->param( 'name' );

my @gd = conn::get_data($conn::DB_NAME{user}, "users", (
    username => $name,
));

unless ( scalar @gd ) {
    print $q->header( -type => 'text/html', -status => '400 Bad Request' );
    print <<EOM;
<h1>400 Bad Request</h1>
<p>
    User '$name' does not exist. <br>
    <a href='./index.cgi'>Home</a>
</p>
EOM
    exit(1);
}

my %hs = %{$gd[0]};
my @allstatus = conn::get_data($conn::DB_NAME{status}, "status", (
    UID => $hs{ID}
));

@allstatus = sort { $b->{ultime} <=> $a->{ultime} } @allstatus;

for my $l (0..scalar(@allstatus)-1) {
    my %h = %{$allstatus[$l]};
    my @lks = conn::get_data($conn::DB_NAME{likes}, "likes", (
        Status_ID => $h{ID}
    ));

    $allstatus[$l]{like_count} = scalar(@lks);
    $allstatus[$l]{have_i_liked} = scalar(
        grep { %$_{Liker_ID} == $det{ID} } @lks
    );
}

print $q->header( 'text/html' );

print Template::parse(Template::readfile('user.html'), {
    uname => $hs{username},
    email => $hs{email},
    allstatus => [@allstatus],
    root => {
        %det
    }
}, {});