/* run with gp -q rsa_factoring.gp (after apt install pari-gp) */
n = 510143758735509025530880200653196460532653147;
t0 = getwalltime();
f = factorint(n);
t = (getwalltime() - t0) / 1000.0;
printf("%.2f\n", t);
print(f);
quit();
