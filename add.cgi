#!/usr/bin/perl

use strict;
use warnings;
use CGI qw/:standard/;
#use CGI::Carp qw/ fatalsToBrowser warningsToBrowser/;
use DBI;
require '/home/bif724_161a18/public_html/Assignment1/tash_a1_lib.pl'; # subroutines containing html code
require '/home/bif724_161a18/.secret';

# password for making connection to mysql, stored as variable after calling subroutine
my $password = get_paswd();
# handle that makes connection to database or prints error message
my $dbh =DBI->connect("DBI:mysql:host=db-mysql;database=bif724_161a18", "bif724_161a18", $password) or die "Problem connecting" . DBI->errstr;

# grabs data from html form
if(param()) {
    # validates submitted form
    my $re1_id = param("re1_id");
    my $score = param("score");
    my $target_gene_id = param("target_id");
    my $re1_position = param("position");
    my $strand = param("strand");
    my $description = param("desc");
    my @error_mess; # stores error messages, if form filled out with incorrect data
    my $check_dups = 1; 
    my $dup_count = 0;
    my $sth;
    my @dups;
    # validates re1_id
    if ($re1_id !~ /(opossum|human|rat|xenopus|chicken)_42_(\d{1,2}[a-z]?)_((W|X|Y|Z)|([1-9]|[1-7][0-9])|scaffold_\d{1,7})_(\d{1,9})_(r|f)/) {
        push @error_mess, "improperly formatted RE1 ID"; #[1-9]|[1-7][0-9] 
        ## Also need to check for duplicates!
        $check_dups = 0; # set to 0 to prevent next if statement execution, if re1_id is invalid - there is no need
                         # to check whether it's in the table already!
    }
    # sql statement to see if re1 id exists within database already
    if ($check_dups == 1) { # means re1_id entered is valid
        my $count = "select count(*) from a1_data where re1_id = ?"; # statement to see if it exists already
        $sth = $dbh->prepare($count) or die "problem with prepare in primary duplicate check" . DBI->errstr;
        $dup_count = $sth->execute($re1_id); # if it exists value will be 1 (defintely not 0)
        @dups = $sth->fetchrow_array;
    } 
    if ($dups[0] !=0) {
        push @error_mess, "this is a duplicate re1 id";  
    }
    # validates score value (must be greater than 0.9100 but less than 1 (to 4 decimal places))
    if ($score !~ /(1)|(0\.9[1-9]{1,3})/) {
        push @error_mess, "improperly formatted score value";
    }
    # validates target gene id
    if ($target_gene_id !~ /((ENS\w{3}G|ENSG)\d{11})/) {
        push @error_mess, "improperly formatted target gene id";
        ## Also need cross-checked
    }
    # validates position 
    if ($re1_position !~ /(3'|5'|exon(\+)?|intron(\+)?)/i) {
        push @error_mess, "invalid position";
    }
    # validates strand value
    if ($strand !~ /(\+|\-)/) {
        push @error_mess, "invalid strand value";
    }
    # validates that no special characters are valid in description box
    if ($description =~ /[\'\"\,\\]/g) {
        push @error_mess, "description contains invalid characters, please remove any ' \" , \ from text";
    }
    if (@error_mess) {
        print "Content-type: text/html\n\n";
        # makes new tab heading, includes css file
        print begin_html("Add a Record - Entry Error!", "tash_a1_add.css");
        foreach (@error_mess) {
            print "<div class='error'><font color='#670046'>error: $_<br></div>";
        }
        print form();
    }
    else {
        # command for sql
        my $sql = "insert into a1_data values (?,?,?,?,?,?)";
        # prepares command
        my $sth = $dbh->prepare($sql) or die "problem with prepare" . DBI->errstr;
        my $rows = $sth->execute($re1_id,$score,$target_gene_id,$re1_position,$strand,$description);
        # if $rows contains data - route page to the view.cgi program
        if ($rows == 1) {
            print "Location: http://zenit.senecac.on.ca/~bif724_161a18/Assignment1/tash_a1_view.cgi?sort=new\n\n";  
        } else {
            print "couldn't insert data\n";
        }
        # drops connection to database and displays error if problem
        $dbh->disconnect() or die "Problem with disconnect" . DBI->errstr;
    }   
}
else {
    # form not submitted, so display form
    print "Content-type: text/html\n\n";
    print begin_html("Add a Record", "tash_a1_add.css");
    print form();
}
print end_html();
sub form {
    my $re1_id = param('re1_id');
    my $score = param('score');
    my $target_gene_id = param('target_id');
    my $position = param('position');
    my $strand = param('strand');
    my $positive = $strand eq '+'?"checked":"";
    my $negative = $strand eq '-'?"checked":"";
    my $description = param('descr'); 
    return<<FORM
    <form action="$0" method="post">
    <div class="table">
    <table class="add">
        <tr><td>RE1 ID</td><td><input type ="text" class="textbox" name ="re1_id" placeholder="e.g. chicken_42_2_1_72260197_r" value = "$re1_id"</td></tr>
        <tr><td>Score</td><td><input type ="text" class="textbox" name ="score" placeholder="e.g. 0.9832" value = "$score"</td></tr>
        <tr><td>Target Gene ID</td><td><input type ="text" class="textbox" name ="target_id" placeholder="e.g. ENSGALG00000019260" value ="$target_gene_id"</td></tr>
        <tr><td>Position</td><td><input type ="text" class="textbox" name ="position" placeholder="e.g. 3'" value = "$position"</td></tr>
        <tr><td>Strand</td><td>positive <input type ="radio" name ="strand" value = "+" $positive>negative <input type ="radio" name ="strand" value = "-" $negative></tr></td>
        <tr><td>Description</td><td><textarea name ="desc" class="textbox" placeholder="Enter in a description, if available">$description</textarea>
        </td></tr><tr><td></td><td colspan = "2" align = "right"><input type ="submit"></td></tr> 
    </table>
    </div>
    </form>
    <div class="form_instruction">
        <h3>Instructions for adding a record</h3>
        <p>Each field will be validated when attempting to submit an entry into the database.
            If one or more of the fields does not meet the required criteria, a helpful error will be returned.
        </p>    
        <ul class="instructions">
            <li>The RE1 id is structured as follows, each separated by an '_':
            </li>
                <ul>
                    <li>one of five accepted species names (e.g. rat/chicken/human/opossum/xenopus)</li>
                    <li>the ensembl database number used (e.g. 42)</li>
                    <li>the name of the region (e.g. chromosome number/W/X/Y/Z/scaffold_ (scaffold is followed by 1-7 digits)</li>
                    <li>the position of the region (e.g. between 1-9 digits)</li>
                    <li>the forward or reverse strand (e.g. f/r)</li>
                </ul>
            <li>The score value must be greater than or equal to 0.9100 but less than of equal to 1, measured to up to 4 decimal places</li>
            <li>Each target gene id begins with 'ENS' and then is structured as either:
                <ul>
                    <li>followed by a 'G' and then 11 digits for the species human</li>
                    <li>followed by three additional letters, then a 'G' and 11 digits</li>
                </ul>
            <li>The re1 position is case-insensitive and contains one of the following:
                <ul>
                 <li> e.g. 3'/5'/intron/exon/intron+/exon+</li>
                </ul>
            <li>The strand type is either negative or positive</li>
            <li>Adding a description is optional, but it cannot contain special characters (e.g. ' " , \ /)</li>   
        </ul>
    </div>
FORM

}


