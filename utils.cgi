#!/usr/bin/perl

package util;

use CGI;

my $q = new CGI;

my %mime_types = (
    'html'           => 'text/html',
    'css'            => 'text/css',
    'javascript'     => 'application/javascript',
    'json'           => 'application/json',
    'xml'            => 'application/xml',
    'plain text'     => 'text/plain',
    'csv'            => 'text/csv',
    'jpeg'           => 'image/jpeg',
    'png'            => 'image/png',
    'gif'            => 'image/gif',
    'svg'            => 'image/svg+xml',
    'ico'            => 'image/x-icon',
    'webp'           => 'image/webp',
    'bmp'            => 'image/bmp',
    'mp3'            => 'audio/mpeg',
    'wav'            => 'audio/wav',
    'ogg audio'      => 'audio/ogg',
    'aac'            => 'audio/aac',
    'midi'           => 'audio/midi',
    'mp4'            => 'video/mp4',
    'webm'           => 'video/webm',
    'ogg video'      => 'video/ogg',
    'avi'            => 'video/x-msvideo',
    'mpeg'           => 'video/mpeg',
    'pdf'            => 'application/pdf',
    'zip'            => 'application/zip',
    'gzip'           => 'application/gzip',
    'microsoft word' => 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'microsoft excel'=> 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'microsoft powerpoint' => 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'binary file'    => 'application/octet-stream',
    'tar'            => 'application/x-tar',
    '7z'             => 'application/x-7z-compressed',
    'ttf'            => 'font/ttf',
    'otf'            => 'font/otf',
    'woff'           => 'font/woff',
    'woff2'          => 'font/woff2',
    'eot'            => 'application/vnd.ms-fontobject'
);

sub open_html {
    my $fl = shift;
    open (HTML_FILE, "<", $fl) || die "Cannot open $fl\n";

    while (my $line = <HTML_FILE>) {
        print $line;
    }

    close (HTML_FILE);
};

sub open_file {
    my $name = shift;
    my @filesp = split /\./, $name;

    my $t = $filesp[$#filesp];
    print $q->header ($mime_types{$t});

    open (FILE_HANDLE, "<", $name);

    while (my $line = <FILE_HANDLE>) {
        print $line;
    }

    close (FILE_HANDLE);
}

sub append_to_file {
    my $fname = shift;
    my $cont = shift;

    open (DB_F, ">>", $fname);
    print DB_F $cont . "\n";
    close (DB_F);
};

sub trim {
    my $data = shift;
    $data =~ s/^\s+|\s+$//g;
    return $data;
}

1;