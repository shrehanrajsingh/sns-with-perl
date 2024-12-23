#!/usr/bin/perl

do './conn.cgi';

use CGI;

my $q = new CGI;

# if ( conn::create_table($conn::DB_NAME{user}, "users", (
#     ID => "Int",
#     username => "String",
#     email => "String",
#     passwd => "String"
# )) ) {
#     print "$conn::LAST_ERROR\n";
# }

# if ( conn::create_table($conn::DB_NAME{status}, "status", (
#     ID => "Int",
#     UID => "Int",
#     content => "String",
#     ultime => "String"
# )) ) {
#     print "$conn::LAST_ERROR\n";
# }

# if ( conn::create_table($conn::DB_NAME{likes}, "likes", (
#     ID => "Int",
#     Status_ID => "Int",
#     Liker_ID => "Int",
#     Like_Type => "String", # L: like, D: dislike
#     ltime => "String"
# ))) {
#     print "$conn::LAST_ERROR\n";
# }

# if ( conn::column_exists($conn::DB_NAME{user}, "users", "username") ) {
#     print "Column exists\n";
# }

# if ( conn::add_data($conn::DB_NAME{user}, "users", (
#     ID => conn::primkey($conn::DB_NAME{user}, "users"),
#     username => "shrehanrajsingh",
#     email => 'shrehanofficial@gmail.com',
#     passwd => conn::encrypt_btwp("123456789")
# )) ) {
#     print "$conn::LAST_ERROR\n";
# }

# my @gt = conn::get_data($conn::DB_NAME{user}, "users", (
#     username => "shrehanrajsingh",
#     email => 'shrehanofficial@gmail.com'
# ));

# for my $i (0..scalar(@gt)-1) {
#     my %p = %{ $gt[$i] };

#     print "index $i\n";
#     for my $j (keys %p) {
#         print "\t$j: $p{$j}\n";
#     }
# }

if ( $q->request_method eq 'GET' 
     and $q->self_url =~ /\bdb_setup.cgi\b/) {

    print $q->header ( -type => "text/html", -status => "405 Not Allowed" );
}