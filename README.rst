============
Pilgrim
============

*Smiles go for (nautical) miles!*

**Pilgrim** is a tool to convert ROMhacks of the European (EU) release of *Pokémon Mystery Dungeon: Explorers of Sky* (EoS) into ROMhacks of the North American (NA) release. It aims to do this while minimizing the amount of copyrighted material that must be copied over, and with as little user input as possible. The user must provide:

- An unmodified (vanilla) EU ROM.
- An unmodified (vanilla) NA ROM.
- A modified EU ROM.

Using these, and some additional user input depending on what modifications the user has made, Pilgrim will create an NA ROM with the same modifications made from the vanilla EU ROM to the modified EU ROM.

A gentler introduction: What's the point of Pilgrim?
""""""""""""""""""""""""""""""""""""""""""""""""""""

This section aims to explain things starting from a very minimal level of ROMhacking knowledge. Feel free to skip reading any questions you already know the answer to!

What's a patch?
***************
For those who have never played a ROMhack; the way ROMhacks are distributed are through patches, which store only the changes made from a base ROM to a modified ROM. To apply a patch, the player must provide the same base ROM that the hack was made with that they legally acquired. By doing it this way, we minimize the amount of copyrighted material that must be distributed.

What's a **conversion** patch?
******************************
A conversion patch is a patch that uses one region's release as the "base ROM", and a different region's base as the "modified ROM".

What's the issue with conversion patches?
*****************************************
While somewhat more legal than pirating a ROM outright, conversion patches still usually involve distribution of copyrighted assets. For example, the EU release of EoS contains dialogue for Spanish, French, German, and Italian, but these translations are entirely absent from the NA release. A conversion patch for NA to EU would distribute all of this copyrighted text. Unlike standard patches, conversion patches are much more legally gray, and while some communities don't mind their usage, `others <https://github.com/ArchipelagoMW/Archipelago>`_ look down upon the practice.

How does Pilgrim address this issue?
************************************
Pilgrim aims to provide a more legally sound alternative to conversion patches. Using a vanilla EU ROM, a vanilla NA ROM, and a modified EU ROM, it creates a ROM based on vanilla NA that has all the changes that were made in the hack. In simpler terms, it 'ports' a ROMhack to the NA release. This allows a patch to be made for the hack with an NA base that *doesn't* distribute any copyrighted assets.

License
"""""""
Pilgrim is licensed under `GPLv3 <https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3>`_, because it has GPLv3 dependencies (`skytemple-files <https://github.com/SkyTemple/skytemple-files>`_ and `ndspy <https://github.com/RoadrunnerWMC/ndspy>`_). Its **source code**, however, is licensed under `MIT <https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT>`_. Refer to https://chesyon.me/eos-licenses.html for info on what this means.