#!/usr/bin/env python
# -*- coding: utf-8 -*-



# print('loading nltk...')
# print datetime.now()
# import nltk
# print datetime.now()

# import cProfile
# cProfile.run('analyze_text()')

# python -m cProfile text_analysis_profiling.py



from text_analysis import analyze_text

html = u"""KABUL, Afghanistan — Outgunned by the Taliban and often derided by some as little more than uniformed thieves, police officers in Afghanistan do not have an easy job. But in recent months, their lives have gotten even tougher: Afghanistan’s police officers have not been paid since November, and some have not seen a paycheck since October.
The government has the money, which comes from the United States and its NATO allies, but the Interior Ministry, which oversees the police, missed a deadline for filing the necessary forms with the Finance Ministry, said Afghan officials interviewed Sunday. The back salaries will be paid in the next few days, the officials said, playing down the issue as a minor administrative mix-up.
Missed deadlines and late paychecks are small problems compared with a festering insurgency, endemic corruption and a thriving illicit opium industry. But the case of the unpaid police officers exemplifies another glaring and often overlooked failure in the American-led nation-building effort here: weak government institutions staffed by officials who are often unqualified or, in some cases, incompetent.
Western officials, in this case, were caught off guard. Despite the billions of dollars their countries spend to pay the police, many American and European officials were not aware that the police had not been paid for nearly two months. They first heard about it when contacted by a reporter on Sunday.
Keeping track of billions in aid money was a problem when Western officials basically ran the Afghan government, and the challenge appears to be getting only worse as the American and European roles diminish.
The few foreign officials who did know about the pay problem said that they had found out about it only in recent days, a month after the last salaries were supposed to be paid, and that they were still trying to figure out what had happened.
It appeared to be a genuinely bureaucratic issue, they said. There were no indications that the money had been stolen or misspent, which is a real concern in Afghanistan.
“The money is in Afghanistan’s treasury,” said Basil Massey, who runs the United Nations trust fund through which the police salaries are transferred to the Afghan government from donor nations. The trust fund was only now becoming aware of the problem because it was reconciling its books from the past quarter, which ended in December.
Some Afghan and Western officials noted that missing or late paychecks had been a problem across the Afghan government for years. But the problem tended to affect one department at a time, not leave roughly 150,000 armed men unpaid in a country with a history of police corruption and factional violence.
In interviews across Afghanistan, nearly two dozen police officers, including rank-and-file constables and senior commanders, said the delay had cut across all the various forces, including the regular uniformed police and the village militias, known as Afghan Local Police, which have well-documented problems with brutality and theft.
A member of a front-line paramilitary unit fighting the Taliban in southern Afghanistan had to ask his family for money to buy necessities, like soap. A police commander gave one of his men $20 — a princely sum for most Afghans — to pay a doctor’s bill for the man’s ailing wife. And, in at least two districts, unpaid police officers appear to have begun demanding money from shop owners and villagers, Afghan and Western officials said.
It is hard to say whether the police were extorting money from people because they had not been paid, the officials said. The Afghan police have a track record of such behavior even when they are paid on time.
“But given that history, isn’t that a reason we should be on top of this?” said an official from the American-led coalition, who would comment on the matter only if not identified while publicly criticizing colleagues. “It’s the police! This should be automatic. You don’t let the police not be paid.”
Many police officers, including commanders, blamed the United States for their late paychecks, adding to the litany of Afghan complaints against their American allies. The disgruntled police officers claimed that the United States was withholding the money to press President Hamid Karzai of Afghanistan into signing a long-term security deal that would allow foreign troops to remain here beyond 2014.
One of the chief reasons the NATO allies want to keep some forces in Afghanistan is to help the Afghan Army and the police master logistics, which includes paying salaries on time.
In any case, payments to the United Nations trust fund are made months in advance, making it impossible for the United States to withhold money so quickly, Afghan and American officials said.
But stories of American bullying resonate in Afghanistan these days. And on Sunday night, a policeman guarding a street in Kabul lined with Western embassies angrily told colleagues that the Americans were withholding the money to weaken Islam and that they should be driven out.
Other officers, though, looked no further than their own government to assign blame. “I stand here every day in this cold weather from morning to evening without being paid,” said one, who gave his name as Assadullah, while directing traffic in Kabul. “I see high-ranking officials passing by in their cars. They do not care.”
On Sunday evening, a suicide bomber on a motorcycle rammed into a bus carrying police officers through Kabul, killing two, officials said. The Taliban claimed responsibility for the attack, which served as a reminder of the very real dangers faced by the Afghan police.
Afghan officials, meanwhile, blamed one another for the problem.
Omar Zakhilwal, the finance minister, said the Interior Ministry’s paperwork arrived three days before the end of the Afghan fiscal year on Dec. 20. By then, the ministry’s processing system was already closed so the accounting books could be reconciled.
Mr. Zakhilwal has been scrutinized for years over allegations of corruption, and he emphasized that the rules were followed without exception at his ministry. The Interior Ministry “might as well have complained about us because we didn’t process their late requests,” he wrote in an email. “But we at the Ministry of Finance follow standard budgetary procedures — and that we stick to.”
Now that the ministry is again dispersing money, the police will soon receive their back pay, he said.
Sediq Sediqqi, a spokesman for the Interior Ministry, said his ministry had missed the deadline because of a shift in the dates for the fiscal year, although that change was announced more than a year ago.
The late paychecks affected only a few areas and were “not a big problem,” Mr. Sediqqi added.
He laughed when asked if he had been paid. “Of course,” he said.
A few hours later, his boss, Umar Daudzai, the interior minister, said in an interview that the entire police force had not been paid in December and that officers in six provinces had also not been paid in November.
Mr. Daudzai, who took over the Interior Ministry last year, said he had already fired a number of officials. “This will not happen again,” he said.
"""

text, data, metrics = analyze_text(html)