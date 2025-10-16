{
  default(realprecision, 10);
  maxtime = 3600; \\ seconds
  bitlist = [64, 128, 192, 224, 240, 256, 264, 272, 280];
  print("Bits\tTime(s)\n");

  for(i = 1, #bitlist,
    bitlen = bitlist[i];
    p = randomprime(2^(bitlen/2));
    q = randomprime(2^(bitlen/2));
    n = p * q;

    t0 = getwalltime();
    f = factorint(n);
    t = (getwalltime() - t0) / 1000.0;

    printf("%d\t%.2f\n", bitlen, t);
    if (t > maxtime, quit());
  );
}
